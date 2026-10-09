# Evidence

## 1. HR baseline import — personally executed

On October 9, 2026, the learner ran the Python HR import and supplied [a screenshot of the successful output](01-hr-baseline-import.png). The import calculated baseline access for seven fictional identities. Alex (E100), in Finance, received `email.user` and `erp.invoice.read`; Jamie (E101), in IT, received `email.user` and `helpdesk.agent`.

The output confirms a saved baseline preview and explicitly states that no application accounts were created or changed. This validates the baseline calculation exercise, not live provisioning, persistent lifecycle reconciliation, or other governance workflows. The screenshot includes local machine paths but no credentials.

## 2. Department-change preview — personally executed

On October 9, 2026, the learner changed Alex's department to IT and reran the import. The supplied [successful output](02-department-change-preview.png) shows E100 retained, with `email.user` and `helpdesk.agent` as the calculated baseline, and without `erp.invoice.read`. Seven identities were processed. This demonstrates recalculation from changed HR attributes; it does not demonstrate provisioning or a recorded revocation. The console does not display manager ID, so the screenshot alone does not validate the manager change.

## 3. Leaver baseline preview — personally executed

On October 9, 2026, the learner reran the import after terminating Taylor (E102). The [supplied output](03-leaver-baseline-preview.png) shows Taylor retained in the seven-identity result with access listed as `none`. This validates an empty calculated baseline for the leaver, not downstream account deactivation or persistent revocation. No live application accounts were changed.

## 4. Joiner baseline preview — personally executed

On October 9, 2026, the learner added Sam Employee (E103) and reran the import. The [supplied output](04-joiner-baseline-preview.png) shows eight identities and Sam's Finance baseline of `email.user` and `erp.invoice.read`. Alex remains in IT and Taylor still has no calculated access. This validates baseline calculation for a new HR identity, not downstream account creation.

## 5. Additional access request — personally executed

The learner created request REQ-d893f6a67266 for Sam (E103), requesting `erp.payment.create` with a business reason. The [supplied screenshot](05-payment-request-pending.png) shows two pending stages (manager and application owner), both assigned to Morgan (E900), and access granted NO. This demonstrates request capture and routing, not approval or provisioning.

## 6. Manager approval — personally executed

The learner recorded Morgan's manager approval for REQ-d893f6a67266. The [supplied output](06-manager-approved.png) shows manager approved, application owner pending, request PENDING, and access granted NO. Reviewer IDs are simulated inputs; there is no authenticated reviewer session.

## 7. Application-owner approval and simulated grant — personally executed

The learner completed Morgan's application-owner approval for REQ-d893f6a67266. The [supplied output](07-owner-approved-simulated-grant.png) shows both stages approved, status APPROVED, and access granted YES (simulated) for `erp.payment.create`. The grant is stored locally in the request record; no live application account changed. This is not yet evidence of a blocked SoD conflict or lifecycle revocation of request-based access.

## 8–9. Conflicting payment permission blocked — personally executed

For request REQ-821a47fc2cbe (`erp.payment.approve` for Sam), the learner first [completed the manager stage](08-conflict-manager-approved.png), then attempted application-owner approval. The [final grant attempt was rejected](09-sod-grant-blocked.png) with SOD-001: the same person cannot create and approve payments. The policy checks the existing simulated payment-creation grant before assigning the conflicting entitlement. Rejection leaves the request pending with no payment-approval grant; it does not record an owner denial or a persisted conflict event. No live application changed.

## 10. Conflicting request closed with denial — personally executed

The learner recorded an explicit owner denial for REQ-821a47fc2cbe, citing SOD-001 and Sam's existing payment-creation access. The [supplied output](10-conflicting-request-denied.png) shows status DENIED, manager approved, application owner denied, and access granted NO. This completes the conflicting-request exercise while preserving the separate approval decisions and denial reason.

## 11. Additional-access certification scope — personally executed

The learner listed active request-based grants for certification. The [supplied output](11-certification-review-scope.png) shows one grant: Sam (E103), `erp.payment.create`, original request REQ-d893f6a67266, manager E900. Baseline permissions are explicitly excluded. This is a review listing, not a completed certification decision or a scheduled campaign.

## 12. Certification revocation — personally executed

The learner recorded review CERT-d6a3db8a0c32 for Sam's payment-creation grant, with Morgan (E900) selecting revoke because Sam no longer handles payment preparation. The [supplied output](12-certification-revoked.png) shows status REVOKED, access granted NO, and removal completed YES (simulated). The certification event and grant removal are saved in the same local request record. A subsequent assistant verification listed zero active request-based grants. Baseline permissions are outside this certification scope; no live application changed.

## 13. Revocation verified — personally executed

The learner reran the certification list command. The [supplied output](13-no-active-additional-grants.png) confirms zero active request-based grants. This verifies the stored revocation rather than merely a decision message.

## 14. Persistent baseline initialized — personally executed

The learner ran HR reconciliation for the first time. The [supplied output](14-baseline-state-initialized.png) shows eight initial-import records and a saved baseline state and history. Alex starts in IT, Sam starts in Finance, and terminated Taylor has no baseline access. No removal is claimed for Taylor because this is the initial state, not a comparison with an earlier active state. Request-based grants are outside this reconciliation step.

## 15. Mover reconciled against saved state — personally executed

The learner transferred Sam (E103) from Finance to IT and ran reconciliation. The [supplied output](15-mover-reconciled.png) shows one HR-change record, adding `helpdesk.agent` and removing `erp.invoice.read`. Assistant inspection of the saved state confirms `email.user` retained, department IT, and manager E901. This is persistent simulated baseline reconciliation, not live provisioning or request-based lifecycle handling.

## 16. Leaver baseline removals reconciled — personally executed

The learner terminated Sam (E103) and ran reconciliation. The [supplied output](16-leaver-reconciled.png) shows one HR-change record with no additions and removal of `email.user` and `helpdesk.agent`. This demonstrates stored baseline removal on termination. Repeat-import verification is pending; request-based lifecycle revocation is outside this step.

## 17. Repeat reconciliation — personally executed

The learner reran reconciliation without HR changes. The [supplied output](17-repeat-reconciliation-no-changes.png) shows eight identities, zero change records, and existing access and history retained. Together with evidence 16, this verifies that terminated Sam's removed baseline access is not recreated by an unchanged repeat import. Request-based lifecycle handling remains outside this step.

## 18. Joiner reconciled into saved state — personally executed

The learner added Avery (E104) in Sales and ran reconciliation. The [supplied output](18-joiner-reconciled.png) shows nine identities and one initial-import record adding `crm.user` and `email.user`, with no removals. This completes the personally executed baseline Joiner/Mover/Leaver reconciliation exercises. These are local simulated access changes, not live provisioning.

## 19. Additional access prepared for lifecycle test — personally executed

The learner created REQ-560bf5786581 for Avery (E104), requesting `erp.invoice.read`. The [supplied output](19-avery-additional-access-request.png) shows status PENDING, Casey Sales (E902) as manager reviewer, Morgan Finance (E900) as application-owner reviewer, and no grant. This prepares the integrated lifecycle exercise; termination revocation has not yet been demonstrated for this request.

## 20–21. Avery's additional access approved — personally executed

The learner [approved the manager stage as Casey (E902)](20-avery-manager-approved.png), leaving access ungranted, then [approved the owner stage as Morgan (E900)](21-avery-owner-granted.png). REQ-560bf5786581 is APPROVED with a simulated `erp.invoice.read` grant. This demonstrates distinct reviewers and establishes additional access for the termination exercise; no live account changed.

## 22. Integrated termination revocation — personally executed

The learner terminated Avery (E104) in HR and ran reconciliation. The [supplied output](22-integrated-leaver-revocation.png) shows removal of baseline `crm.user` and `email.user`, plus one request lifecycle change revoking `erp.invoice.read` on REQ-560bf5786581 for HR termination. Assistant inspection confirms an empty saved baseline and request status revoked with access_granted false. This validates local termination revocation across both access sources. Pending-request cancellation and additional-access transfer revocation have automated checks but are not yet personally demonstrated.

## 23. Integrated repeat reconciliation — personally executed

The learner reran reconciliation after Avery's termination with no further HR edits. The [supplied output](23-integrated-repeat-no-changes.png) shows nine identities, zero baseline change records, and zero request lifecycle changes. Together with evidence 22, this verifies stable removal across baseline and request-based access on a repeat import.

## 24. Pending request prepared for transfer cancellation — personally executed

The learner created REQ-7a22aaa430a7 for Jamie (E101), requesting `crm.user` while in IT. The [supplied output](24-jamie-pending-before-transfer.png) shows both approval stages pending, manager Riley (E901), owner Casey (E902), and no access granted. This establishes the pre-transfer pending request; cancellation is not yet demonstrated.

## 25. Transfer cancels pending request — personally executed

The [supplied output](25-transfer-cancels-pending-request.png) shows Jamie's transfer adding invoice read, removing helpdesk access, and cancelling REQ-7a22aaa430a7 for department transfer. Saved history confirms email retained. Two HR records changed: Alex's manager changed from E901 to E900 while Jamie's department changed to Finance but manager remained E901. The cancellation succeeded; correction of the manager fields to the intended mapping is the next exercise.

## 26. Manager assignments corrected — personally executed

The learner corrected the manager fields and reran reconciliation. The [supplied output](26-manager-assignments-corrected.png) shows two HR-change records without access additions/removals and zero request lifecycle changes. Assistant verification confirms Alex (E100), IT, manager E901, and Jamie (E101), Finance, manager E900. The prior cancelled request remains closed.
