"""Create pending simulated requests; this step never grants access."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid

from import_hr import ROOT, calculate_access


def create_request(employee_id, entitlement, reason, identities, catalog):
    identity = identities.get(employee_id)
    if not identity or identity["status"] != "active":
        raise ValueError("Requests require an active HR identity")
    permission = catalog["entitlements"].get(entitlement)
    if not permission or not permission.get("requestable"):
        raise ValueError("Entitlement is not requestable")
    if entitlement in identity["baseline_access"]:
        raise ValueError("Identity already has this baseline access")
    if not reason.strip():
        raise ValueError("A business reason is required")
    stages = []
    for stage, reviewer in [("manager", identity["manager_id"]),
                            ("application_owner", permission["owner"])]:
        if reviewer == employee_id:
            reviewer = "E999"
        if reviewer == employee_id or reviewer not in identities or identities[reviewer]["status"] != "active":
            raise ValueError(f"No eligible reviewer for {stage}")
        stages.append({"stage": stage, "reviewer_id": reviewer, "decision": "pending"})
    return {"request_id": "REQ-" + uuid.uuid4().hex[:12],
            "employee_id": employee_id, "entitlement": entitlement,
            "business_reason": reason.strip(), "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "department_at_request": identity["department"],
            "approval_stages": stages, "access_granted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--employee", required=True)
    parser.add_argument("--entitlement", required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    path = ROOT / "runtime/access-requests.json"
    try:
        identities = calculate_access(ROOT / "data/hr-feed.csv", ROOT / "data/access-catalog.json")["identities"]
        catalog = json.loads((ROOT / "data/access-catalog.json").read_text(encoding="utf-8-sig"))
        request = create_request(args.employee, args.entitlement, args.reason, identities, catalog)
        requests = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        if any(r["employee_id"] == args.employee and r["entitlement"] == args.entitlement
               and r["status"] == "pending" for r in requests):
            raise ValueError("A pending request already exists for this identity and entitlement")
        requests.append(request)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(requests, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Request rejected: {error}\n")
    print(f"Request: {request['request_id']}")
    print(f"Employee: {args.employee} | {identities[args.employee]['display_name']}")
    print(f"Entitlement: {args.entitlement}")
    print(f"Business reason: {request['business_reason']}")
    print("Status: PENDING")
    for stage in request["approval_stages"]:
        reviewer = identities[stage["reviewer_id"]]
        print(f"Approval stage: {stage['stage']} | {stage['reviewer_id']} | {reviewer['display_name']} | pending")
    print("Access granted: NO")
    print("Simulation only. Complete manager and owner reviews separately; this command grants no access.")


if __name__ == "__main__":
    main()
