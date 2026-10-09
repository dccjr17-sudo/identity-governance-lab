"""Record a simulated manager decision. Application-owner approval follows later."""

import argparse
from datetime import datetime, timezone
import json

from import_hr import ROOT, calculate_access


def review_manager(request, reviewer_id, decision, reason, identities, catalog):
    if request["status"] != "pending":
        raise ValueError("Request is no longer pending")
    if decision not in {"approve", "deny"} or not reason.strip():
        raise ValueError("A valid decision and review reason are required")
    employee = identities.get(request["employee_id"])
    reviewer = identities.get(reviewer_id)
    if not employee or employee["status"] != "active":
        raise ValueError("Requester is no longer active")
    if not reviewer or reviewer["status"] != "active":
        raise ValueError("Reviewer must be active")
    if reviewer_id == request["employee_id"]:
        raise ValueError("Self approval is prohibited")
    stage = next(s for s in request["approval_stages"] if s["stage"] == "manager")
    expected = employee["manager_id"]
    if expected == request["employee_id"]:
        expected = "E999"
    if reviewer_id != stage["reviewer_id"] or reviewer_id != expected:
        raise ValueError("Reviewer is not the assigned current manager")
    if employee["department"] != request["department_at_request"]:
        raise ValueError("Department changed; request must be reassessed")
    permission = catalog["entitlements"].get(request["entitlement"])
    if not permission or not permission.get("requestable"):
        raise ValueError("Entitlement is no longer requestable")
    if stage["decision"] != "pending":
        raise ValueError("Manager decision has already been recorded")
    stage.update(decision="approved" if decision == "approve" else "denied",
                 reviewed_by=reviewer_id, reason=reason.strip(),
                 reviewed_at=datetime.now(timezone.utc).isoformat())
    if decision == "deny":
        request["status"] = "denied"
    request["access_granted"] = False
    return request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--decision", choices=["approve", "deny"], required=True)
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
        review_manager(request, args.reviewer, args.decision, args.reason, identities, catalog)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(requests, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    except (ValueError, KeyError, OSError, StopIteration) as error:
        parser.exit(1, f"Review rejected: {error}\n")
    print(f"Request: {request['request_id']}")
    print(f"Status: {request['status'].upper()}")
    for stage in request["approval_stages"]:
        print(f"Approval stage: {stage['stage']} | {stage['reviewer_id']} | {stage['decision']}")
    print("Access granted: NO")
    print("Simulation only: reviewer ID is a lab input, not an authenticated login.")


if __name__ == "__main__":
    main()
