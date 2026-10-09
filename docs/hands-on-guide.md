# Hands-on guide

## Phase 1: Understand the identity source

Open `data/hr-feed.csv`. Employee ID is the stable correlation key; names and departments can change. The manager ID identifies who reviews business need. Worker type distinguishes employees from contractors. Status will drive deactivation.

Answer these before implementing the import:

1. Who approves Alex's business need for additional access?
2. What should happen to Alex's Finance access if HR moves him to IT?
3. Why should the employee ID remain unchanged during that transfer?

Expected answers: Morgan Finance (E900); remove obsolete Finance baseline access and reassess additional access; preserve correlation and the identity's audit history.

## Phase 2: Map access

A role bundles access for a business function. An entitlement is a specific permission in an application. Finance baseline includes email and invoice read access. Payment creation and payment approval are additional permissions, not baseline privileges.

## Phase 3: Request and approve

Alex requests payment creation with a business reason. Keep it pending until both approval stages complete. Reject unauthorized reviewers and self approval. Record decisions, reviewers, reasons, and timestamps. Recheck policies when granting access, because access may have changed since the request was submitted.

## Phase 4: Certify

Create a review of current access for managers. Keep required access and revoke access that is no longer justified. Record each reviewed identity, entitlement, decision, reviewer, reason, and completed removal. A certification revocation must not silently return on the next HR import; the implementation must explicitly handle baseline policy exceptions.

## Phase 5: Exercise lifecycle events

- Joiner: add a fictional employee and assign the appropriate department baseline.
- Mover: transfer Alex from Finance to IT. Remove Finance access and invalidate pending requests tied to the former role. Reassess previously approved additional access.
- Leaver: terminate Taylor. Remove all access and cancel pending requests. Reimport the same feed to verify access remains removed.

## Phase 6: Test separation of duties

Grant Alex payment creation after approval. Request payment approval and verify the conflict is blocked. Also seed an existing conflicting assignment in a controlled test and detect it during a review. Test both directions of the conflict.

## Evidence and publication

The final portfolio should contain executable source, repeatable tests, actual results, an architecture diagram, and a short explanation of business risk. Label automated results separately from exercises personally completed. Do not describe the simulation as hands-on SailPoint product experience.
