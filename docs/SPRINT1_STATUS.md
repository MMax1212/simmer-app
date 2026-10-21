# Sprint 1 acceptance coverage

Baseline: the approved `spec.md` and `intent.md` in this branch, plus
`Sprint_Plan_1.md`. This change aligns John's Sprint 1 implementation with those
contracts and adds regression and integration coverage.

| Requirement | Implementation / verification |
|---|---|
| Registration, unique accounts, username-or-email login, JWT + user payload | Versioned auth routes; auth tests and browser onboarding |
| Password hashing and no plaintext password responses | New Argon2 hashes, legacy bcrypt verification/upgrade; Unicode/long-password and response-redaction regressions |
| Admin RBAC, account status and roles | Guarded endpoints and screens; denied access, escalation, self-change, deactivate/reactivate and role-change tests |
| Admin audit flags | Persistent before/after audit rows for management changes; database assertions |
| Profile bio, avatar and culinary preferences | PUT profile endpoint, HTTP(S) URL validation, null normalization; API and rendered-form tests |
| Recipe metadata, ingredient amounts and units | Contract fields stored and displayed; persistence and invalid-input tests |
| Ordered recipe steps and dynamic forms | Relational step rows, consecutive numbering, add/remove controls; API, frontend and Chromium tests |
| Empty ingredients/steps rejected | Server and client validation; regression tests |
| Personal recipe library, pagination and details | Author-filtered list with offset/limit, paginated cards, ordered detail display; cross-user, UI and browser tests |
| Expired/malformed token handling | Backend 401; client clears token/auth state and protected routes redirect; API/frontend/browser tests |
| Missing recipe | Backend 404 and displayed error; API/frontend tests |
| Database migrations | Alembic baseline + data-preserving upgrade; fresh, repeated, existing-unversioned and failed-upgrade rollback tests |
| Frontend stack | React 18, TypeScript, React Router, Vite, Tailwind via Vite plugin |
| CI foundation | Separate backend, frontend tests/build and full-browser jobs on push/PR |
| Complete user journey | Real Chromium registration, profile save/reload, recipe create/edit/list/reload/delete, logout and username login |

## Deliberate compatibility and privacy choices

- The authenticated profile/token/admin responses include email and role as specified.
  The optional public profile lookup retains the previous privacy behavior and omits
  these private fields; Sprint 1 does not introduce public social sharing.
- New recipe submissions require complete, positive ingredient measurements. Unknown
  legacy amounts/units are preserved as null in read responses so the migration never
  invents measurements or makes existing recipes unreadable. Repair them when editing.
- Metadata fields named by spec.md are included even though categorization also appears
  in the release plan's Sprint 2 scope. Advanced search, social features, uploads,
  grocery lists, Docker/PostgreSQL integration and deployment are outside this change.
- The documented database defaults (0-minute timings, 1 serving, medium difficulty)
  replace legacy null defaults. Existing instruction text is preserved verbatim.
- Setting required status checks, approving the team's scope and accepting the sprint
  remain repository-admin/product-owner decisions; passing tests is not product acceptance.
