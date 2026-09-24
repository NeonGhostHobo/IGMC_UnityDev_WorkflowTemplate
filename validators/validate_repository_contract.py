#!/usr/bin/env python3
"""Validate an installed IGMC v2 repository contract without external packages."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    pass


def fail(message: str) -> None:
    raise ContractError(message)


def json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def validate_schema(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected is not None:
        expected_types = [expected] if isinstance(expected, str) else expected
        if not any(json_type_matches(value, item) for item in expected_types):
            errors.append(f"{path}: expected {' or '.join(expected_types)}, got {type(value).__name__}")
            return errors

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']!r}")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than {schema['minLength']}")
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(pattern, value) is None:
            errors.append(f"{path}: value {value!r} does not match {pattern!r}")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: array has fewer than {schema['minItems']} items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: array items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_schema(item, item_schema, f"{path}[{index}]"))

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for required in schema.get("required", []):
            if required not in value:
                errors.append(f"{path}: missing required property {required!r}")
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in properties:
                errors.extend(validate_schema(item, properties[key], f"{path}.{key}"))
            elif additional is False:
                errors.append(f"{path}: unexpected property {key!r}")
            elif isinstance(additional, dict):
                errors.extend(validate_schema(item, additional, f"{path}.{key}"))
    return errors


def load_json(path: Path, description: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        fail(f"Missing {description}: {path}")
        raise AssertionError from exc
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {description} {path}: {exc}")
        raise AssertionError from exc


def validate_contract(root: Path) -> None:
    contract_path = root / ".igmc" / "repository.json"
    schema_path = root / ".igmc" / "schema" / "repository.schema.json"
    contract = load_json(contract_path, "repository contract")
    schema = load_json(schema_path, "repository contract schema")
    errors = validate_schema(contract, schema)

    if isinstance(contract, dict):
        paths = contract.get("paths", {})
        if isinstance(paths, dict):
            for name in ("documentation", "design", "tickets"):
                relative = paths.get(name)
                if isinstance(relative, str):
                    candidate = (root / relative).resolve()
                    try:
                        candidate.relative_to(root.resolve())
                    except ValueError:
                        errors.append(f"$.paths.{name}: path escapes repository root")
                    if not candidate.exists():
                        errors.append(f"$.paths.{name}: declared path does not exist: {relative}")

        enabled = contract.get("skills", {}).get("enabled", []) if isinstance(contract.get("skills"), dict) else []
        for skill in enabled if isinstance(enabled, list) else []:
            skill_path = root / ".agents" / "skills" / str(skill) / "SKILL.md"
            if not skill_path.is_file():
                errors.append(f"$.skills.enabled: missing skill entrypoint {skill_path.relative_to(root)}")

    if errors:
        fail("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an IGMC v2 repository contract.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    args = parser.parse_args()
    try:
        validate_contract(Path(args.root).resolve())
    except ContractError as exc:
        print(f"REPOSITORY CONTRACT VALIDATION FAIL:\n{exc}")
        return 1
    print("Repository contract validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
