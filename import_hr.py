"""Preview HR-derived baseline access. No live accounts are changed."""

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def calculate_access(feed_path, catalog_path):
    catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8-sig"))
    roles = catalog["department_roles"]
    known_entitlements = catalog["entitlements"]
    for department, permissions in roles.items():
        if any(permission not in known_entitlements for permission in permissions):
            raise ValueError(f"Unknown entitlement in {department} role")
    with Path(feed_path).open(newline="", encoding="utf-8-sig") as feed:
        reader = csv.DictReader(feed)
        required = {"employee_id", "display_name", "department", "job_title",
                    "manager_id", "worker_type", "status"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("HR feed is missing required columns")
        rows = list(reader)
    identities = {}
    for row in rows:
        if any(row.get(field) is None for field in required):
            raise ValueError("Incomplete HR record")
        identity = {field: row[field].strip() for field in sorted(required)}
        employee_id = identity["employee_id"]
        if not employee_id or not identity["display_name"]:
            raise ValueError("Employee ID and display name are required")
        if employee_id in identities:
            raise ValueError(f"Duplicate employee ID: {employee_id}")
        if identity["status"] not in {"active", "terminated"}:
            raise ValueError(f"Unsupported status for {employee_id}")
        if identity["department"] not in roles:
            raise ValueError(f"Unknown department for {employee_id}")
        identity["baseline_access"] = (
            sorted(set(roles[identity["department"]]))
            if identity["status"] == "active" else []
        )
        identities[employee_id] = identity
    for employee_id, identity in identities.items():
        manager = identity["manager_id"]
        if manager and (manager not in identities or manager == employee_id):
            raise ValueError(f"Invalid manager relationship for {employee_id}")
    return {"mode": "baseline-preview", "identity_count": len(identities),
            "identities": identities}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feed", type=Path, default=ROOT / "data/hr-feed.csv")
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/access-catalog.json")
    parser.add_argument("--output", type=Path, default=ROOT / "runtime/baseline-preview.json")
    args = parser.parse_args()
    try:
        result = calculate_access(args.feed, args.catalog)
    except (ValueError, KeyError, OSError, csv.Error) as error:
        parser.exit(1, f"Import rejected: {error}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Calculated baseline access for {result['identity_count']} fictional identities.\n")
    for employee_id, identity in result["identities"].items():
        access = ", ".join(identity["baseline_access"]) or "none"
        print(f"{employee_id} | {identity['display_name']} | {identity['department']} | {access}")
    print(f"\nSaved preview: {args.output}")
    print("Simulation only: no application accounts were created or changed.")


if __name__ == "__main__":
    main()
