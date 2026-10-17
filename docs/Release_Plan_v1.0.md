# Release Plan — CSE 115a Software Engineering

**Document Name:** Release Plan  
**Product Name:** Simmer  
**Team Name:** Team Simmer (Maximo Mora, Bryan Moreno, Ulises Diaz, John Weaver, Benjamin Ong)  
**Release Name:** Simmer MVP (v1.0)  
**Release Date:** December 11, 2026 *(Target End of Sprint 4)*  
**Revision:** 1.2  
**Revision Date:** October 11, 2026  

---

## 1. High-Level Goals

- **Goal 1 (User Authentication & Identity):** Enable new users to register, securely log in, and manage personal profiles with culinary preferences.
- **Goal 2 (Recipe Authoring & Management):** Allow users to create, categorize, edit, and organize personal recipes with structured ingredients and tool specifications.
- **Goal 3 (Recipe Discovery & Search):** Provide rich search and multi-criteria filtering capabilities (dietary, cooking time, occasion) to easily find recipes.
- **Goal 4 (Social Sharing & Community Engagement):** Enable users to share food posts, interact through likes and comments, bookmark favorites, and follow fellow home chefs.
- **Goal 5 (Technical Architecture & Extensibility):** Establish a modular, scalable architecture (database schemas, REST/GraphQL APIs, CI/CD pipeline) as a foundation for future releases.

---

## 2. Release Scope by Sprint

*Every item is labeled with its **Item Type** (Feature Story, Infrastructure, or Spike) and its **Associated High-Level Goal**.*

### Sprint 1: Architecture Bootstrap, User Accounts & Recipe Authoring
*Focus: Tooling acquisition, environment setup, exploratory research on media storage, and core authentication.*

| Priority | ID | Type | Assoc. Goal | User Story / Task Description | Points |
| :---: | :---: | :---: | :---: | :--- | :---: |
| **{P1}** | **INF-1.1** | Infrastructure | **Goal 5** | **Infrastructure:** Initialize Git monorepo, branch protection rulesets, Vite + FastAPI scaffold, and CI linting pipelines. | **3** |
| **{P2}** | **SPK-1.1** | Spike | **Goal 2** | **Spike:** Research and prototype cloud image upload and storage strategies (Cloudinary vs. AWS S3 vs. local static) for recipe images in Sprint 2. | **2** |
| **{P1}** | **US1.1** | Feature | **Goal 1** | **As a user**, I want to register for a personal account so that I can securely log in and access personalized features. | **5** |
| **{P1}** | **US1.2** | Feature | **Goal 1** | **As an administrator**, I want an admin role and management panel so that I can moderate accounts and assist users. | **5** |
| **{P1}** | **US1.3** | Feature | **Goal 1** | **As a user**, I want to edit my profile (bio, avatar, dietary preferences) so that my culinary identity is current for the community. | **3** |
| **{P1}** | **US1.4** | Feature | **Goal 2** | **As a user**, I want to create and save new recipes with instructions and cook times so that I can store my favorite dishes. | **5** |

**Sprint 1 Breakdown:** Feature Stories: 18 pts | Infrastructure: 3 pts | Spikes: 2 pts  
**Sprint 1 Total: 23 Points** *(Includes 5 pts of foundational enablers — see Sanity Check)*

---

### Sprint 2: Categorization, Structured Ingredients & Search
*Focus: Deepening recipe data structures, search algorithms, and preparing social feed architecture.*

| Priority | ID | Type | Assoc. Goal | User Story / Task Description | Points |
| :---: | :---: | :---: | :---: | :--- | :---: |
| **{P2}** | **SPK-2.1** | Spike | **Goal 4** | **Spike:** Evaluate social activity feed data models (relational queries vs. timeline caching) in preparation for Sprint 3 interactions. | **2** |
| **{P1}** | **US2.1** | Feature | **Goal 2** | **As a user**, I want to categorize recipes by cuisine, meal type, and difficulty so that my collection remains organized. | **3** |
| **{P1}** | **US2.2** | Feature | **Goal 3** | **As a user**, I want to search recipes by title and keywords so that I can quickly locate specific meals. | **5** |
| **{P1}** | **US2.3** | Feature | **Goal 2** | **As a user**, I want to mark and log recipes I have completed so that I can track my cooking history. | **3** |
| **{P2}** | **US2.4** | Feature | **Goal 2** | **As a user**, I want to specify structured ingredient lists and required kitchen tools so that I know what is needed before cooking. | **5** |

**Sprint 2 Breakdown:** Feature Stories: 16 pts | Spikes: 2 pts  
**Sprint 2 Total: 18 Points**

---

### Sprint 3: Social Feed, Interactions & Following
*Focus: Public social feed, comment/like micro-interactions, bookmarks, and grocery list algorithm research.*

| Priority | ID | Type | Assoc. Goal | User Story / Task Description | Points |
| :---: | :---: | :---: | :---: | :--- | :---: |
| **{P2}** | **SPK-3.1** | Spike | **Goal 3** | **Spike:** Research grocery checklist aggregation logic (ingredient name normalization & fractional unit addition) for Sprint 4. | **2** |
| **{P1}** | **US3.1** | Feature | **Goal 4** | **As a user**, I want to publish posts with food photos, recipe links, and descriptions so that I can share my culinary creations. | **5** |
| **{P1}** | **US3.2** | Feature | **Goal 4** | **As a user**, I want to edit or delete my existing posts so that I can correct mistakes or remove unwanted content. | **3** |
| **{P1}** | **US3.3** | Feature | **Goal 4** | **As a user**, I want to like and comment on community posts so that I can engage with other food creators. | **5** |
| **{P2}** | **US3.4** | Feature | **Goal 4** | **As a user**, I want to bookmark public posts into a "Saved Posts" collection so that I can revisit inspiring ideas later. | **3** |
| **{P2}** | **US3.5** | Feature | **Goal 4** | **As a user**, I want to follow other users so that their new recipes and posts appear on my home feed. | **3** |

**Sprint 3 Breakdown:** Feature Stories: 19 pts | Spikes: 2 pts  
**Sprint 3 Total: 21 Points**

---

### Sprint 4: Discovery, Filtering, Grocery Checklist & Production Release
*Focus: Friend discovery, smart recipe filtering, grocery checklists, and final production staging.*

| Priority | ID | Type | Assoc. Goal | User Story / Task Description | Points |
| :---: | :---: | :---: | :---: | :--- | :---: |
| **{P1}** | **INF-4.1** | Infrastructure | **Goal 5** | **Infrastructure:** Production staging deployment (cloud database migration, environment secret management, and final build optimization). | **3** |
| **{P1}** | **US4.1** | Feature | **Goal 4** | **As a user**, I want to find and connect with friends via username search so that I can build my culinary network. | **5** |
| **{P1}** | **US4.2** | Feature | **Goal 2** | **As a user**, I want to generate an aggregated grocery checklist from selected recipes so that I know what to purchase at the store. | **5** |
| **{P2}** | **US4.3** | Feature | **Goal 3** | **As a user**, I want to browse a personalized discovery feed of trending recipes so that I can explore new culinary ideas. | **5** |
| **{P2}** | **US4.4** | Feature | **Goal 3** | **As a user**, I want to filter recipes by dietary tags (low-calorie, vegan) and occasions (quick dinner, date night) so that I find meals tailored to my needs. | **5** |

**Sprint 4 Breakdown:** Feature Stories: 20 pts | Infrastructure: 3 pts  
**Sprint 4 Total: 23 Points**

---

## 3. Release Summary by Item Type

| Sprint | Milestone Focus | Features | Infra | Spikes | Total Points |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **Sprint 1** | Repo Bootstrap, CI/CD, Image Storage Spike, Auth & Recipe Creation | 18 pts | 3 pts | 2 pts | **23 pts** |
| **Sprint 2** | Categorization, Search, Ingredient Lists & Feed Architecture Spike | 16 pts | 0 pts | 2 pts | **18 pts** |
| **Sprint 3** | Social Feed, Post Authoring, Comments/Likes & Grocery Algorithm Spike | 19 pts | 0 pts | 2 pts | **21 pts** |
| **Sprint 4** | Friend Connections, Smart Filtering, Grocery Utility & Cloud Deployment | 20 pts | 3 pts | 0 pts | **23 pts** |
| **Total** | **Release 1.0 Cumulative Workload** | **73 pts** | **6 pts** | **6 pts** | **85 pts** |

---

## 4. Sanity Check & Capacity Analysis

### Team Velocity & Capacity
- **Team Size:** 5 developers (Maximo Mora, Bryan Moreno, Ulises Diaz, John Weaver, Benjamin Ong).
- **Nominal Velocity:** ~20–21 story points per 2-week sprint ($4\text{ pts/developer/sprint}$).
- **Total Release Capacity across 4 Sprints:** $4 \times 21 \text{ pts} = 84 \text{ story points}$.
- **Planned Workload:** 85 story points (73 pts features + 6 pts infrastructure + 6 pts spikes). This is within 1 point of team capacity.

### Explicit Allowances for Infrastructure & Spikes
1. **Sprint 1 Tooling & Spikes:** Setting up Git branch rulesets, Vite, FastAPI, and investigating recipe image storage (**INF-1.1** and **SPK-1.1**, totaling 5 pts) are explicitly separated from feature stories so the team does not suffer hidden technical debt.
2. **Sprint 2 Exam Buffer:** Sprint 2 contains only 16 feature points and 1 small spike (18 pts total) to accommodate university midterm examinations.
3. **Mid-Course Adjustments:** If velocity drops below 20 pts/sprint, non-critical {P2} stories (such as **US4.3 Discovery Feed** [5 pts] or **US4.4 Smart Filters** [5 pts]) will be cleanly descoped to the product backlog without impacting the core high-level release goals.

---

## 5. Product Backlog (Deferred Features)

| Priority | ID | Assoc. Goal | User Story | Points |
| :---: | :---: | :---: | :--- | :---: |
| {P2} | PB-01 | Goal 2 | As a user, I want to automatically parse and generate ingredient lists from recipe photos using AI. | 8 |
| {P2} | PB-02 | Goal 2 | As a user, I want an integrated multi-timer tool so that I can track multiple cooking stages. | 2 |
| {P3} | PB-03 | Goal 2 | As a user, I want to discover and save beverage & cocktail recipes. | 3 |
| {P2} | PB-04 | Goal 4 | As a user, I want to send direct messages and share recipes privately with friends. | 8 |
| {P2} | PB-05 | Goal 4 | As a user, I want to receive push notifications when users interact with my posts. | 5 |
| {P2} | PB-06 | Goal 4 | As a user, I want to share posts to external social media platforms (Instagram, Twitter). | 3 |
| {P2} | PB-07 | Goal 4 | As a user, I want to pin selected posts to the top of my profile. | 2 |
| {P2} | PB-08 | Goal 4 | As a user, I want to add audio/music tracks to my recipe video posts. | 5 |
| {P2} | PB-09 | Goal 4 | As a user, I want to organize and RSVP to cooking meetups with friends. | 8 |
| {P2} | PB-10 | Goal 3 | As a user, I want to locate nearby restaurants and food markets on an interactive map. | 5 |
| {P2} | PB-11 | Goal 3 | As a user, I want to write ratings and reviews for local restaurants. | 5 |
| {P2} | PB-12 | Goal 3 | As a user, I want to save favorite restaurants to my profile. | 3 |
| {P2} | PB-13 | Goal 4 | As a user, I want to view other food creators' favorite restaurants and dishes. | 5 |
| {P3} | PB-14 | Goal 4 | As a user, I want to earn culinary badges and achievements for milestone recipes. | 5 |
| {P3} | PB-15 | Goal 4 | As a user, I want to maintain a weekly cooking streak counter to stay motivated. | 5 |
| {P3} | PB-16 | Goal 3 | As a user, I want an ML-powered recommendation engine based on past interaction history. | 8 |
