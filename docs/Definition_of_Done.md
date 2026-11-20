# Definition of Done (DoD)
**Project:** Simmer | **Team:** Team Simmer | **Version:** 1.1 | **Date:** Nov 19, 2026

---

## 1. Task-Level Definition of Done
*"Did we build the thing right?" (Engineering & Code Quality Perspective)*

A task is considered **Done** when ALL of the following criteria are met:
- [ ] **Branch & Commits:** Code is committed with clear, imperative commit messages and pushed to the dedicated feature/task branch.
- [ ] **Full-Stack Build Integrity:**
  - Frontend builds with zero TypeScript errors or bundling warnings (`npm run build`).
  - Backend database migrations apply cleanly without errors (`alembic upgrade head`).
- [ ] **Automated Test Verification:**
  - All unit/component tests in the frontend test suite pass 100% (`npm test`).
  - All backend unit/integration tests pass 100% (`python -m pytest -q`).
- [ ] **Peer Code Review:** Pull request has been reviewed, commented on, and approved by at least one other team member.
- [ ] **CI Pipeline Green:** All GitHub Actions automated checks (Backend, Frontend, and Browser tests) pass completely.
- [ ] **Documentation:** Any new external/public REST API endpoints, schemas, or environment variable changes are documented in the `README.md` and `docs/API_README.md`.

---

## 2. User Story-Level Definition of Done
*"Did we build the right thing?" (Product & User Value Perspective)*

A user story is considered **Done** when ALL of the following criteria are met:
- [ ] **Task Completion:** All sub-tasks belonging to the story are completed and marked Done on the Scrum Task Board.
- [ ] **Acceptance Criteria Verification:** All acceptance criteria scenarios outlined in the Sprint Plan and `intent.md` pass verification.
- [ ] **Zero Regression:** No breaking changes or regressions introduced to existing features across the full test suite.
- [ ] **Merged to Main:** Feature branch is cleanly merged into `main` via an approved Pull Request.
