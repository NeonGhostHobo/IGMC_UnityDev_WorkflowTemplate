from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPLY = ROOT / "apply.py"
STANDARD_VALIDATOR = ROOT / "validators" / "validate_standard_assets.py"
sys.path.insert(0, str(ROOT / "validators"))
from validate_repository_contract import validate_schema  # noqa: E402


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd or ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


class WorkflowTests(unittest.TestCase):
    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            result = run(str(APPLY), "--dest", str(destination), "--repo-id", "dry-run")
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn('"mode": "plan"', result.stdout)
            self.assertEqual(list(destination.iterdir()), [])

    def test_apply_installs_codex_core_and_valid_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            result = run(
                str(APPLY),
                "--dest",
                str(destination),
                "--repo-id",
                "smoke",
                "--repo-name",
                'Smoke "Repository"',
                "--archetype",
                "generic-software",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            contract = json.loads((destination / ".igmc" / "repository.json").read_text(encoding="utf-8"))
            self.assertEqual(contract["repository"]["id"], "smoke")
            self.assertEqual(contract["repository"]["name"], 'Smoke "Repository"')
            self.assertEqual(contract["standard"]["version"], "2.0.0")
            self.assertFalse(contract["automation"]["unattended_ai"])
            self.assertFalse((destination / ".github").exists())
            self.assertTrue((destination / ".agents" / "skills" / "igmc-work" / "SKILL.md").is_file())
            validator = run(str(destination / "scripts" / "validate_repository_contract.py"), ".", cwd=destination)
            self.assertEqual(validator.returncode, 0, validator.stdout)
            manifests = list((destination / ".igmc" / "migrations").glob("*-scaffold.json"))
            self.assertEqual(len(manifests), 1)
            manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
            manifest_schema = json.loads(
                (ROOT / "standard" / "schemas" / "migration-manifest.schema.json").read_text(encoding="utf-8")
            )
            self.assertEqual(validate_schema(manifest, manifest_schema), [])

    def test_invalid_default_repository_id_is_rejected_before_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="invalid repository ") as directory:
            destination = Path(directory)
            result = run(str(APPLY), "--dest", str(destination), "--apply")
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("Rendered repository contract is invalid", result.stdout)
            self.assertEqual(list(destination.iterdir()), [])

    def test_conflict_blocks_complete_apply_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            initial = run(str(APPLY), "--dest", str(destination), "--repo-id", "conflict", "--apply")
            self.assertEqual(initial.returncode, 0, initial.stdout)
            agents = destination / "AGENTS.md"
            agents.write_text("local instructions\n", encoding="utf-8")
            missing = destination / ".agents" / "skills" / "igmc-review" / "SKILL.md"
            missing.unlink()

            result = run(str(APPLY), "--dest", str(destination), "--apply")
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertEqual(agents.read_text(encoding="utf-8"), "local instructions\n")
            self.assertFalse(missing.exists(), "preflight failure must prevent partial writes")

            forced = run(str(APPLY), "--dest", str(destination), "--apply", "--force")
            self.assertEqual(forced.returncode, 0, forced.stdout)
            self.assertNotEqual(agents.read_text(encoding="utf-8"), "local instructions\n")
            self.assertTrue(missing.exists())
            latest_manifest = sorted((destination / ".igmc" / "migrations").glob("*-scaffold.json"))[-1]
            manifest = json.loads(latest_manifest.read_text(encoding="utf-8"))
            self.assertIn("overwrite", {operation["action"] for operation in manifest["operations"]})

    def test_contract_validator_rejects_cost_policy_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            initial = run(str(APPLY), "--dest", str(destination), "--repo-id", "invalid", "--apply")
            self.assertEqual(initial.returncode, 0, initial.stdout)
            contract_path = destination / ".igmc" / "repository.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["automation"]["unattended_ai"] = True
            contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
            validator = run(str(destination / "scripts" / "validate_repository_contract.py"), ".", cwd=destination)
            self.assertEqual(validator.returncode, 1, validator.stdout)
            self.assertIn("expected constant False", validator.stdout)

    def test_github_adapters_are_explicit_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            result = run(
                str(APPLY),
                "--dest",
                str(destination),
                "--repo-id",
                "github-opt-in",
                "--with-github-ci",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            workflow = destination / ".github" / "workflows" / "igmc-contract.yml"
            self.assertTrue(workflow.is_file())
            text = workflow.read_text(encoding="utf-8").lower()
            self.assertNotIn("openai", text)
            self.assertNotIn("codex exec", text)
            self.assertNotIn("schedule:", text)
            self.assertIn("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1", text)

    def test_issue_publication_requires_explicit_external_write_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "issue.md"
            draft.write_text(
                """# IGMC: Verify explicit publication

Schema version: 1.0
Type: maintenance
Area: workflow
Status: proposed

## Summary

Keep publication explicit.

## Acceptance criteria

- [ ] Publication needs confirmation.

## Validation

- Run the issue validator.

## Sources

- User request.

## Dependencies

- None.
""",
                encoding="utf-8",
            )
            check = run(str(ROOT / "template" / "scripts" / "igmc_issue.py"), "check", str(draft))
            self.assertEqual(check.returncode, 0, check.stdout)
            publish = run(str(ROOT / "template" / "scripts" / "igmc_issue.py"), "publish", str(draft))
            self.assertEqual(publish.returncode, 1, publish.stdout)
            self.assertIn("--confirm-external-write", publish.stdout)

    def test_standard_assets_and_distribution_coverage(self) -> None:
        result = run(str(STANDARD_VALIDATOR))
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
