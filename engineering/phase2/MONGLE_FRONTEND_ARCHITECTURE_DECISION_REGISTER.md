# MONGLE Frontend Architecture Decision Register

Task: `MONGLE-W6-FRONTEND-TARGET-ARCHITECTURE-DESIGN-001`

## ADR-FE-001 — Top-level layer model
Status: PROPOSED_FOR_PM_REVIEW. Context: measured pages/platform/shared overlap. Decision: adopt app, pages, platform, services, shared as a target contract. Alternatives: keep current roots only; feature folders without platform. Reason: separates composition, route screens, cross-service capability, service ownership and neutral reuse. Consequence: no immediate moves. Migration impact: incremental only.

## ADR-FE-002 — One-screen-one-page
Status: PROPOSED_FOR_PM_REVIEW. Context: route reachability needs a single entry. Decision: one approved route screen has `pages/<Page>/index.tsx`. Alternatives: route directly to service components; multi-page screen directory. Reason: makes route ownership auditable. Consequence: page-local components stay local. Migration impact: applies to new approved screens first.

## ADR-FE-003 — Platform versus service
Status: PROPOSED_FOR_PM_REVIEW. Decision: family-wide auth/account/family/access/shell/navigation are platform; Markpoint, Doran/Wagle, calendar, tasks, album and ledger are services. Alternatives: all modules under platform; all under shared. Reason: prevents service models becoming cross-service coupling. Consequence: requires authority decision before moving current files. Migration impact: no current move.

## ADR-FE-004 — Shared promotion
Status: PROPOSED_FOR_PM_REVIEW. Decision: promote only after two actual equal-contract consumers. Alternatives: predictive shared library; duplicate everything. Reason: measured shared already has domain coupling. Consequence: page/service-local by default. Migration impact: review after second consumer.

## ADR-FE-005 — Service dependency
Status: PROPOSED_FOR_PM_REVIEW. Decision: services cannot import one another; app composition or platform contracts mediate. Alternatives: direct service imports; shared service model. Reason: keeps calendar/tasks/album/ledger independently addable. Consequence: cross-service use needs explicit contract. Migration impact: enforce in scaffold/import checks.

## ADR-FE-006 — Registry ownership
Status: PROPOSED_FOR_PM_REVIEW. Decision: app owns a declarative service registry. Alternatives: App hardcodes all services; shell owns registry. Reason: measured shell/router drift. Consequence: no registry file until scaffold authority. Migration impact: registry starts with first approved service migration.

## ADR-FE-007 — Route/navigation consistency
Status: PROPOSED_FOR_PM_REVIEW. Decision: route, navigation item and access policy derive from or validate against one registry declaration. Alternatives: separate manually maintained lists. Reason: four observed linked-but-unregistered routes. Consequence: hidden/disabled state is explicit; unregistered visible destinations fail validation. Migration impact: repair only in a dedicated route task.

## ADR-FE-008 — Auth reverse dependency
Status: PROPOSED_FOR_PM_REVIEW. Decision: migrate auth store/contracts to platform/auth; retain neutral transport only in shared. Alternatives: platform contract types only; shared generic types. Reason: store consumers make it platform capability; shared-to-page import violates direction. Consequence: type and import changes are deferred. Migration impact: one authority-approved auth task.

## ADR-FE-009 — Preview-to-final-page
Status: PROPOSED_FOR_PM_REVIEW. Decision: 1c preview remains task-owned until GPT Visual Gate and route/product authority. Alternatives: immediately relocate preview; treat preview as final page. Reason: current route is explicitly preview-only. Consequence: no source separation now. Migration impact: separate post-gate task.

## ADR-FE-010 — Incremental migration
Status: PROPOSED_FOR_PM_REVIEW. Decision: preserve active implementation; migrate one approved authority and its route/API contract at a time. Alternatives: big-bang restructure; directory-only scaffold. Reason: active legacy routes and duplicate candidates. Consequence: tree conformity never outranks product authority. Migration impact: each task records source-to-target mapping and removes no old authority without approval.
