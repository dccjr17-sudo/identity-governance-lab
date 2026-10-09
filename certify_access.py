"""Review request-based grants; baseline-access certifications come later."""

import argparse
from datetime import datetime, timezone
import json
import uuid

from import_hr import ROOT, calculate_access


def certify(request, reviewer_id, decision, reason, identities):
    if not request.get("access_granted") or request["status"] != "approved":
        raise ValueError("This request has no active grant to certify")
    if decision not in {"keep", "revoke"} or not reason.strip():
        raise ValueError("A keep/revoke decision and reason are required")
    employee = identities.get(request["employee_id"])
    reviewer = identities.get(reviewer_id)
    if not employee or not reviewer or reviewer["status"] != "active":
        raise ValueError("Identity and active reviewer must exist")
    manager = employee["manager_id"]
    if manager == request["employee_id"]:
        manager = "E999"
    if reviewer_id == request["employee_id"] or reviewer_id != manager:
        raise ValueError("Only the current eligible manager can certify this access")
    if decision == "keep" and (employee["status"] != "active"
                               or employee["department"] != request["department_at_request"]):
        raise ValueError("Changed employment requires reassessment; cannot retain this grant")
    event = {"review_id": "CERT-" + uuid.uuid4().hex[:12], "reviewer_id": reviewer_id,
             "decision": decision, "reason": reason.strip(),
             "reviewed_at": datetime.now(timezone.utc).isoformat(),
             "employee_id": request["employee_id"], "entitlement": request["entitlement"],
             "removal_completed": decision == "revoke"}
    request.setdefault("certification_history", []).append(event)
    if decision == "revoke":
        request["access_granted"] = False
        request["status"] = "revoked"
    return event


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List granted additional access awaiting review")
    review = sub.add_parser("review")
    review.add_argument("--request", required=True)
    review.add_argument("--reviewer", required=True)
    review.add_argument("--decision", required=True, choices=["keep", "revoke"])
    review.add_argument("--reason", required=True)
    args = parser.parse_args()
    path = ROOT / "runtime/access-requests.json"
    try:
        requests = json.loads(path.read_text(encoding="utf-8"))
        identities = calculate_access(ROOT / "data/hr-feed.csv", ROOT / "data/access-catalog.json")["identities"]
        if args.command == "list":
            grants = [r for r in requests if r.get("access_granted")]
            print(f"Additional-access certification scope: {len(grants)} active grant(s)")
            for request in grants:
                identity = identities.get(request["employee_id"])
                manager = identity["manager_id"] if identity else "UNKNOWN"
                print(f"{request['request_id']} | {request['employee_id']} | {request['entitlement']} | manager {manager}")
            print("Scope: request-based grants only; baseline access is excluded from this exercise.")
            return
        request = next((r for r in requests if r["request_id"] == args.request), None)
        if request is None:
            raise ValueError("Request ID was not found")
        event = certify(request, args.reviewer, args.decision, args.reason, identities)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(requests, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Certification rejected: {error}\n")
    print(f"Review: {event['review_id']}\nRequest: {request['request_id']}")
    print(f"Decision: {event['decision'].upper()}\nReviewer: {event['reviewer_id']}")
    print(f"Reason: {event['reason']}\nStatus: {request['status'].upper()}")
    print(f"Access granted: {'YES (simulated)' if request['access_granted'] else 'NO'}")
    print(f"Removal completed: {'YES (simulated)' if event['removal_completed'] else 'Not requested'}")
    print("Simulation only: certification and grant state saved together; no live application changed.")


if __name__ == "__main__":
    main()
