"""Record application-owner decisions and simulated request-based access grants."""

import argparse
from datetime import datetime, timezone
import json

from import_hr import ROOT, calculate_access


def review_owner(request, reviewer_id, decision, reason, identities, catalog, requests):
    if request["status"] != "pending":
        raise ValueError("Request is no longer pending")
    if decision not in {"approve", "deny"} or not reason.strip():
        raise ValueError("A valid decision and reason are required")
    employee = identities.get(request["employee_id"])
    reviewer = identities.get(reviewer_id)
    if not employee or employee["status"] != "active":
        raise ValueError("Requester is no longer active")
    if not reviewer or reviewer["status"] != "active" or reviewer_id == request["employee_id"]:
        raise ValueError("An active reviewer other than the requester is required")
    if employee["department"] != request["department_at_request"]:
        raise ValueError("Department changed; request must be reassessed")
    permission = catalog["entitlements"].get(request["entitlement"])
    if not permission or not permission.get("requestable"):
        raise ValueError("Entitlement is no longer requestable")
    manager_stage = next(s for s in request["approval_stages"] if s["stage"] == "manager")
    owner_stage = next(s for s in request["approval_stages"] if s["stage"] == "application_owner")
    manager_id = employee["manager_id"]
    if manager_id == request["employee_id"]:
        manager_id = "E999"
    if (manager_stage["decision"] != "approved" or manager_stage.get("reviewed_by") != manager_id
            or manager_id == request["employee_id"] or manager_id not in identities
            or identities[manager_id]["status"] != "active"):
        raise ValueError("Approval from the current eligible manager is required first")
    owner_id = permission["owner"]
    if owner_id == request["employee_id"]:
        owner_id = "E999"
    if reviewer_id != owner_id or reviewer_id != owner_stage["reviewer_id"]:
        raise ValueError("Reviewer is not the assigned current application owner")
    if owner_stage["decision"] != "pending":
        raise ValueError("Owner decision has already been recorded")
    if decision == "approve":
        access = set(employee["baseline_access"])
        access.update(r["entitlement"] for r in requests
                      if r["employee_id"] == request["employee_id"] and r.get("access_granted"))
        access.add(request["entitlement"])
        for rule in catalog.get("sod_rules", []):
            if set(rule["incompatible_entitlements"]).issubset(access):
                raise ValueError(f"SoD conflict {rule['id']}: {rule['description']}")
    owner_stage.update(decision="approved" if decision == "approve" else "denied",
                       reviewed_by=reviewer_id, reason=reason.strip(),
                       reviewed_at=datetime.now(timezone.utc).isoformat())
    request["status"] = "approved" if decision == "approve" else "denied"
    request["access_granted"] = decision == "approve"
    return request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--decision", required=True, choices=["approve", "deny"])
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    path = ROOT / "runtime/access-requests.json"
    try:
        requests = json.loads(path.read_text(encoding="utf-8"))
        request = next((r for r in requests if r["request_id"] == args.request), None)
        if request is None:
            raise ValueError("Request ID was not found")
        identities = calculate_access(ROOT / "data/hr-feed.csv", ROOT / "data/access-catalog.json")["identities"]
        catalog = json.loads((ROOT / "data/access-catalog.json").read_text(encoding="utf-8-sig"))
        review_owner(request, args.reviewer, args.decision, args.reason, identities, catalog, requests)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(requests, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    except (ValueError, KeyError, OSError, StopIteration) as error:
        parser.exit(1, f"Review rejected: {error}\n")
    print(f"Request: {request['request_id']}\nStatus: {request['status'].upper()}")
    for stage in request["approval_stages"]:
        print(f"Approval stage: {stage['stage']} | {stage['reviewer_id']} | {stage['decision']}")
    print(f"Access granted: {'YES (simulated)' if request['access_granted'] else 'NO'}")
    print(f"Entitlement: {request['entitlement']}")
    print("Simulation only: grant stored in request record; no live application account changed.")


if __name__ == "__main__":
    main()
