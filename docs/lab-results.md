# Lab results

Guided exercises executed on October 9, 2026. All access changes were simulated locally. The portfolio owner edited HR records, ran commands, and supplied [26 evidence screenshots](../evidence/README.md). Codex assisted with implementation and documentation.

## Demonstrated outcomes

- Sam's payment creation was granted only after manager and owner approval. A conflicting payment-approval grant was blocked by SOD-001 and explicitly denied.
- Morgan revoked Sam's payment-creation access through certification with a reason; subsequent listing showed zero active additional grants.
- Saved baseline reconciliation recorded new joiners, removed obsolete department access on transfer, and removed baseline access on termination.
- Avery's termination revoked both baseline CRM/email and approved additional invoice-reading access. Repeating the import produced zero baseline and request changes.
- Jamie's transfer cancelled a pending CRM request and replaced IT baseline with Finance baseline while retaining email.
- An accidental manager edit was identified in saved attribute history and corrected without changing access (evidence 25–26).

## Automated validation

Run `python -m unittest discover -v` from the repository root. There are 26 distinct tests using isolated fixtures; they do not mutate saved learner state. Coverage includes active identity checks, wrong reviewers, self approval, approval order, terminal denial, changed employment, SoD rejection without state mutation, certification removal, lifecycle cancellation/revocation, and repeat imports.

Additional-grant transfer revocation, pending-request cancellation on termination, and certification keep behavior are tested but not individually demonstrated in screenshots. Baseline certifications, scheduled campaigns, and existing-conflict scanning are not implemented. Reviewer identities are unauthenticated CLI inputs; no production authorization or real SailPoint configuration is claimed.
