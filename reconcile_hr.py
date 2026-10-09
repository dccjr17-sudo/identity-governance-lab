"""Persist simulated baseline access and an append-only history of HR changes.

Also revokes request-based grants and cancels stale pending requests.
"""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json

from import_hr import ROOT, calculate_access


def reconcile_requests(requests, identities):
    updated = deepcopy(requests)
    changes = []
    for request in updated:
        identity = identities.get(request["employee_id"])
        if identity is None:
            continue  # Missing rows are not authoritative termination events.
        reason = None
        if identity["status"] == "terminated":
            reason = "HR termination"
        elif identity["department"] != request["department_at_request"]:
            reason = "HR department transfer; additional access requires reassessment"
        elif request["status"] == "pending":
            manager = identity["manager_id"]
            if manager == request["employee_id"]:
                manager = "E999"
            stage = next(s for s in request["approval_stages"] if s["stage"] == "manager")
            if manager != stage["reviewer_id"]:
                reason = "HR manager change; pending request requires rerouting"
        if reason and (request.get("access_granted") or request["status"] == "pending"):
            action = "revoked" if request.get("access_granted") else "cancelled"
            event = {"recorded_at": datetime.now(timezone.utc).isoformat(),
                     "request_id": request["request_id"], "employee_id": request["employee_id"],
                     "entitlement": request["entitlement"], "action": action, "reason": reason}
            request["access_granted"] = False
            request["status"] = action
            request.setdefault("lifecycle_history", []).append(event)
            changes.append(event)
    return updated, changes


def save_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def reconcile(previous, identities):
    result = deepcopy(previous)
    result.setdefault("identities", {})
    result.setdefault("history", [])
    changes = []
    # An absent HR row is not interpreted as termination.
    for employee_id, identity in identities.items():
        old = result["identities"].get(employee_id)
        before = set(old["baseline_access"]) if old else set()
        after = set(identity["baseline_access"])
        changed_attributes = {field: {"before": old.get(field), "after": identity[field]}
                              for field in identity if field != "baseline_access"
                              and old and old.get(field) != identity[field]}
        if old is None or before != after or changed_attributes:
            event = {"employee_id": employee_id,
                     "event": "initial_import" if old is None else "hr_change",
                     "recorded_at": datetime.now(timezone.utc).isoformat(),
                     "added": sorted(after - before), "removed": sorted(before - after),
                     "retained": sorted(before & after), "attributes": changed_attributes}
            result["history"].append(event)
            changes.append(event)
        result["identities"][employee_id] = deepcopy(identity)
    return result, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feed", default=ROOT / "data/hr-feed.csv")
    args = parser.parse_args()
    path = ROOT / "runtime/baseline-state.json"
    try:
        identities = calculate_access(args.feed, ROOT / "data/access-catalog.json")["identities"]
        previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        result, changes = reconcile(previous, identities)
        request_path = ROOT / "runtime/access-requests.json"
        requests = json.loads(request_path.read_text(encoding="utf-8")) if request_path.exists() else []
        updated_requests, request_changes = reconcile_requests(requests, identities)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Save revocations first. If the baseline save fails, rerunning safely completes it.
        # These two files are not a single database transaction; run one CLI at a time.
        if request_changes:
            save_json(request_path, updated_requests)
        save_json(path, result)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Reconciliation rejected: {error}\n")
    print(f"Reconciled {len(identities)} HR identities | {len(changes)} change record(s)")
    for event in changes:
        print(f"{event['employee_id']} | {event['event']} | added: {', '.join(event['added']) or 'none'} | removed: {', '.join(event['removed']) or 'none'}")
    if not changes:
        print("No changes. Existing access and history retained.")
    print(f"Request lifecycle changes: {len(request_changes)}")
    for event in request_changes:
        print(f"{event['request_id']} | {event['employee_id']} | {event['entitlement']} | {event['action']} | {event['reason']}")
    print(f"Saved baseline state and history: {path}")
    print("Simulation only: baseline and request access reconciled locally; no live application changed.")


if __name__ == "__main__":
    main()
