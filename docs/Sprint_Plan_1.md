# Sprint 1 Plan — CMPS 115 Software Methodology

**Document Name:** Sprint 1 Plan  
**Product Name:** Simmer  
**Team Name:** Team Simmer  
**Sprint Period:** October 12, 2026 – October 25, 2026  
**Sprint Completion Date:** October 25, 2026  
**Revision:** 1.1  
**Revision Date:** October 11, 2026  

---

## 1. Sprint Goal

> **Goal:** Establish the foundational architecture, development environment, and core data models for Simmer, enabling end users and administrators to securely authenticate, configure user profiles, and author/view personal recipes within a dedicated personal recipe library.

---

## 2. Task Listing (Organized by User Story in Priority Order)

*Note: All task estimates conform to the standard guideline of $\le 6$ ideal engineering hours.*

### User Story 1 (Priority {P1} — 5 Story Points)
**US1.1:** *As a user, I want to create an account and log in securely so that I can access personalized features and maintain my personal culinary data.*

- **Task 1.1:** Initialize Git repository, branch protections, and CI/CD development environment — *4 hours*
- **Task 1.2:** Design account registration and login UI mockups/components — *3 hours*
- **Task 1.3:** Create user authentication database schema and migration scripts — *4 hours*
- **Task 1.4:** Implement backend account registration and password hashing logic — *5 hours*
- **Task 1.5:** Implement client-side input validation and dynamic error messaging — *3 hours*
- **Task 1.6:** Integrate frontend registration/login forms with backend authentication API — *5 hours*
- **Task 1.7:** Write and execute automated unit & integration tests for user authentication — *6 hours*  
**Total for User Story 1: 30 hours**

---

### User Story 2 (Priority {P1} — 5 Story Points)
**US1.2:** *As an administrator, I want an admin role and dashboard so that I can manage system settings, review accounts, and assist users.*

- **Task 2.1:** Design administrative navigation and user management console interface — *3 hours*
- **Task 2.2:** Extend database schema with user roles, privileges, and admin audit flags — *3 hours*
- **Task 2.3:** Implement role-based access control (RBAC) middleware and token validation — *4 hours*
- **Task 2.4:** Build admin management API endpoints (view users, flag/edit status) — *5 hours*
- **Task 2.5:** Connect admin frontend view to admin management endpoints with error handling — *3 hours*
- **Task 2.6:** Conduct end-to-end security and role escalation testing — *5 hours*  
**Total for User Story 2: 23 hours**

---

### User Story 3 (Priority {P1} — 3 Story Points)
**US1.3:** *As a user, I want to edit my profile details so that I can keep my personal information and culinary preferences up to date.*

- **Task 3.1:** Design profile view and editable profile settings interface — *3 hours*
- **Task 3.2:** Implement profile update backend endpoint (bio, culinary tags, avatar URL) — *4 hours*
- **Task 3.3:** Connect profile editing form to database via authenticated API calls — *3 hours*
- **Task 3.4:** Add validation rules for profile inputs (character limits, format checks) — *2 hours*
- **Task 3.5:** Write integration test cases for profile retrieval and update workflows — *5 hours*  
**Total for User Story 3: 17 hours**

---

### User Story 4 (Priority {P1} — 5 Story Points)
**US1.4:** *As a user, I want to create and save recipes so that I can reference and prepare them whenever I need.*

- **Task 4.1:** Design recipe authoring interface (title, ingredients, steps, timings) — *3 hours*
- **Task 4.2:** Design and implement relational database schema for recipes and instructions — *4 hours*
- **Task 4.3:** Implement responsive frontend recipe creation and input form — *5 hours*
- **Task 4.4:** Implement backend recipe storage service and validation logic — *5 hours*
- **Task 4.5:** Associate created recipes with author user ID and implement persistence — *4 hours*
- **Task 4.6:** Execute automated tests for multi-step recipe persistence and edge cases — *6 hours*  
**Total for User Story 4: 27 hours**

---

### User Story 5 (Priority {P2} — 3 Story Points)
**US1.5:** *As a user, I want to view my saved recipes in a personal "My Recipes" tab so that I can quickly reference my collection.*

- **Task 5.1:** Design "My Recipes" dashboard tab and card layout — *3 hours*
- **Task 5.2:** Create query endpoints to fetch and paginate user-specific saved recipes — *4 hours*
- **Task 5.3:** Implement frontend state management for saved recipes list — *3 hours*
- **Task 5.4:** Implement full recipe detail modal/view display — *3 hours*
- **Task 5.5:** Test recipe fetching, empty state display, and rendered detail views — *3 hours*  
**Total for User Story 5: 16 hours**

---

## 3. Workload Summary

- **Total Team Workload:** 113 Ideal Engineering Hours
- **Team Size:** 5 Members
- **Average Workload:** $113 \div 5 = 22.6\text{ ideal hours per member}$ across the 2-week sprint (~11.3 hours/week per developer).

---

## 4. Team Roles for Sprint 1

| Team Member | Role(s) | Primary Sprint Responsibilities |
| :--- | :--- | :--- |
| **Maximo Mora** | Product Owner (PO), Full-Stack Developer | Requirements clarification, scope acceptance, frontend auth forms & admin console. |
| **Bryan Moreno** | Scrum Master, DevOps / Backend Developer | Sprint process coordination, Git & CI/CD pipeline, backend auth endpoints & RBAC. |
| **Ulises Diaz** | Frontend Developer, UI/UX Lead | UI/UX component design, responsive styling, profile editing interface & recipe views. |
| **John Weaver** | Database Architect, Backend Developer | Database modeling, schema migrations, recipe API endpoints & query optimization. |
| **Benjamin Ong** | QA & Testing Lead, Developer | Test harness setup, unit/integration test suites, security validation & regression testing. |

---

## 5. Initial Task Assignment

Every team member has been assigned their starting user story and specific initial task for Day 1:

| Team Member | Initial User Story | Initial Task Assignment | Estimated Hours |
| :--- | :--- | :--- | :---: |
| **Bryan Moreno** | **US1.1** (User Auth) | **Task 1.1:** Initialize Git repository, branch protections, and CI/CD environment | 4 hrs |
| **Maximo Mora** | **US1.1** (User Auth) | **Task 1.2:** Design account registration and login UI mockups/components | 3 hrs |
| **John Weaver** | **US1.1** (User Auth) | **Task 1.3:** Create user authentication database schema and migration scripts | 4 hrs |
| **Ulises Diaz** | **US1.3** (Profile) | **Task 3.1:** Design profile view and editable profile settings interface | 3 hrs |
| **Benjamin Ong** | **US1.1** (User Auth) | **Task 1.7:** Write testing scaffold & unit test plan for authentication workflows | 6 hrs |

---

## 6. Initial Burnup Chart

- **Location:** The live digital burnup chart is tracked in the team Jira/GitHub Projects workspace, and a physical duplicate is posted on the team board in the CSE 115 Lab.
- **Sprint Baseline Scope:** 113 ideal hours / 21 story points.
- **Tracking Frequency:** Updated daily during the Daily Scrum to reflect hours completed vs. total sprint commitment.

```
Hours
120 |------------------------------------------------ Total Scope Line (113h)
100 |                                            /
 80 |                                     /
 60 |                              /
 40 |                       /
 20 |                /
  0 +------+------+------+------+------+------+------+
   Day 1  Day 3  Day 5  Day 7  Day 9  Day 11 Day 14
```

---

## 7. Initial Scrum Board (Sprint Task Board)

| User Story | Tasks Not Started | Tasks in Progress | Tasks Completed |
| :--- | :--- | :--- | :---: |
| **US1.1: User Account Registration & Login** *(5 pts)* | • Task 1.4: Implement backend registration logic (5h)<br>• Task 1.5: Input validation & error messages (3h)<br>• Task 1.6: Connect frontend forms to API (5h) | • **Task 1.1:** Init Git repo & CI/CD [Bryan, 4h]<br>• **Task 1.2:** Design registration UI [Maximo, 3h]<br>• **Task 1.3:** Create user DB schema [John, 4h]<br>• **Task 1.7:** Test account creation [Benjamin, 6h] | *None (Day 1)* |
| **US1.2: Admin Account & RBAC** *(5 pts)* | • Task 2.1: Design admin interface (3h)<br>• Task 2.2: Admin DB schema & flags (3h)<br>• Task 2.3: RBAC middleware (4h)<br>• Task 2.4: Admin management API (5h)<br>• Task 2.5: Connect admin frontend (3h)<br>• Task 2.6: Security & role testing (5h) | *(Scheduled after US1.1 foundational auth completes)* | *None (Day 1)* |
| **US1.3: User Profile Management** *(3 pts)* | • Task 3.2: Profile update backend endpoint (4h)<br>• Task 3.3: Connect profile form to DB (3h)<br>• Task 3.4: Profile input validation (2h)<br>• Task 3.5: Integration tests for profile (5h) | • **Task 3.1:** Design profile interface [Ulises, 3h] | *None (Day 1)* |
| **US1.4: Recipe Creation & Saving** *(5 pts)* | • Task 4.1: Design recipe creation UI (3h)<br>• Task 4.2: Recipe DB schema (4h)<br>• Task 4.3: Implement recipe form (5h)<br>• Task 4.4: Recipe saving backend service (5h)<br>• Task 4.5: Connect recipes to user accounts (4h)<br>• Task 4.6: Multi-recipe test suite (6h) | *(Scheduled to start in Week 1, Day 3)* | *None (Day 1)* |
| **US1.5: Personal Recipe Tab** *(3 pts)* | • Task 5.1: Design personal recipe tab (3h)<br>• Task 5.2: Query endpoints for saved recipes (4h)<br>• Task 5.3: Saved recipes state management (3h)<br>• Task 5.4: Recipe detail view (3h)<br>• Task 5.5: Test viewing saved recipes (3h) | *(Scheduled to start in Week 2)* | *None (Day 1)* |

---

## 8. Scrum Meeting Schedule

The team conducts three standups weekly to inspect progress and adapt the sprint backlog:

- **Monday:** 10:30 AM – 11:30 AM (In-person, Engineering Lab)
- **Wednesday:** 10:30 AM – 11:30 AM (In-person, Engineering Lab) — **Official TA / Tutor Lab Check-in Meeting**
- **Friday:** 10:30 AM – 11:30 AM (In-person, Engineering Lab / Hybrid)

**Asynchronous Communication & Overflow:**  
If urgent blockers arise between meetings, the team coordinates via the dedicated Discord/Slack channel. Any rescheduled meetings will be communicated to the TA at least 24 hours in advance.
