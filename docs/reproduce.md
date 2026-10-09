# Reproduce the lab

Use a fresh repository copy with no runtime state. Requires Python 3.10+. Run commands from the root, one at a time. Invoke Python directly if PowerShell blocks the optional launcher.

Copy `data/hr-feed-start.csv` over `data/hr-feed.csv` in this fresh copy. The other feed is the final exercise state. Run:

```text
python import_hr.py
python reconcile_hr.py
```

Add Sam's row to the feed:

```csv
E103,Sam Employee,Finance,Finance Analyst,E900,Employee,active
```

Run reconciliation, then request additional access:

```text
python access_requests.py --employee E103 --entitlement erp.payment.create --reason "Prepare Finance payments"
```

Replace REQUEST_ID below with the generated REQ ID:

```text
python review_request.py --request REQUEST_ID --reviewer E900 --decision approve --reason "Business need confirmed"
python review_owner.py --request REQUEST_ID --reviewer E900 --decision approve --reason "Appropriate permission; no conflict"
```

Manager approval alone grants no access. Owner approval checks SoD before granting simulated access.

Request `erp.payment.approve` for Sam with a test reason, approve its manager stage, then attempt owner approval using its new ID. Expect SOD-001 rejection. Close it with `review_owner.py --decision deny` and a reason.

Review the original payment-creation grant:

```text
python certify_access.py list
python certify_access.py review --request REQUEST_ID --reviewer E900 --decision revoke --reason "Payment duties ended"
python certify_access.py list
```

Expect revoked and zero active additional grants. Transfer Sam to IT, manager E901, then reconcile: add helpdesk, remove invoice read, keep email. Terminate Sam and reconcile: remove email and helpdesk. Repeat: zero changes.

Add Avery's row:

```csv
E104,Avery Employee,Sales,Sales Analyst,E902,Employee,active
```

Reconcile. Request `erp.invoice.read` for E104; approve as manager E902 and owner E900 using its generated ID. Terminate Avery and reconcile: remove baseline CRM/email and revoke the additional invoice-read grant for HR termination. Repeat: zero baseline and request changes.

While Jamie (E101) is in IT, request `crm.user` and leave it pending. Transfer Jamie to Finance, manager E900, then reconcile: remove helpdesk, add invoice read, retain email, cancel the pending request.

Run checks:

```text
python -m unittest discover -v
```

Inspect local `runtime/baseline-state.json` and `runtime/access-requests.json` for histories. Runtime files are excluded from publication. The original personal exercise sequence is documented in the evidence index. No scheduled campaign, baseline certification, or live provisioning is performed.
