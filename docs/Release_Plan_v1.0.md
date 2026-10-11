# Release Plan — CSE 115a Software Engineering

**Document Name:** Release Plan  
**Product Name:** Simmer  
**Team Name:** Team Simmer (Maximo Mora, Bryan Moreno, Ulises Diaz, John Weaver, Benjamin Ong)  
**Release Name:** Simmer MVP (v1.0)  
**Release Date:** December 11, 2026 *(Target End of Sprint 4)*  
**Revision:** 1.1  
**Revision Date:** October 11, 2026  

---

## 1. High-Level Goals

1. **User Authentication & Identity:** Enable new users to register, securely log in, and manage personal profiles with culinary preferences.
2. **Recipe Authoring & Management:** Allow users to create, categorize, edit, and organize personal recipes with ingredient and tool specifications.
3. **Recipe Discovery & Search:** Provide rich search and multi-criteria filtering capabilities (e.g., dietary, cooking time, occasion) to easily find recipes.
4. **Social Sharing & Community Engagement:** Enable users to share food posts, interact through likes and comments, bookmark favorites, and follow fellow home chefs.
5. **Technical Architecture & Extensibility:** Establish a modular, scalable architecture (database schemas, REST/GraphQL APIs, CI/CD pipeline) to serve as a solid foundation for future releases.

---

## 2. User Stories Defining the Scope of the Release

Each user story adheres to the INVEST criteria (*Independent, Negotiable, Valuable, Estimatable, Sized appropriately, Testable*) and is formatted as:  
`{Priority} [Story ID] As a {user role}, I want {goal} so that {reason} [Story Points]`

### Sprint 1: Foundation, User Accounts & Recipe Creation (Target: 18 pts)
*Focus: Environment bootstrap, authentication, basic profile management, and initial recipe authoring.*

| Priority | ID | User Story | Points |
| :---: | :---: | :--- | :---: |
| **{P1}** | **US1.1** | As a user, I want to register for a personal account so that I can securely log in and access personalized features. | **5** |
| **{P1}** | **US1.2** | As an administrator, I want an admin role and management panel so that I can moderate accounts and assist users. | **5** |
| **{P1}** | **US1.3** | As a user, I want to edit my profile (bio, avatar, dietary preferences) so that my culinary identity is current for the community. | **3** |
| **{P1}** | **US1.4** | As a user, I want to create and save new recipes with instructions and cook times so that I can store my favorite dishes. | **5** |
| **{P2}** | **US1.5** | As a user, I want to view my saved recipes in a personal "My Recipes" tab so that I can quickly reference them while cooking. | **3** |

**Sprint 1 Total: 21 Story Points** *(Adjusted to 18 pts capacity by allocating infrastructure buffer — see Sanity Check)*

---

### Sprint 2: Recipe Categorization, Ingredients & Search (Target: 18 pts)
*Focus: Deepening recipe data structure, categorization, tracking, and discoverability.*

| Priority | ID | User Story | Points |
| :---: | :---: | :--- | :---: |
| **{P1}** | **US2.1** | As a user, I want to categorize recipes by cuisine, meal type, and difficulty so that my collection remains organized. | **3** |
| **{P1}** | **US2.2** | As a user, I want to search recipes by title and keywords so that I can quickly locate specific meals. | **5** |
| **{P1}** | **US2.3** | As a user, I want to mark and log recipes I have completed so that I can track my cooking history. | **3** |
| **{P2}** | **US2.4** | As a user, I want to specify structured ingredient lists and required kitchen tools so that I know exactly what is needed before cooking. | **5** |

**Sprint 2 Total: 16 Story Points**

---

### Sprint 3: Social Feed, Interactions & Following (Target: 18 pts)
*Focus: Social community features, public feed, comments, likes, bookmarks, and user follows.*

| Priority | ID | User Story | Points |
| :---: | :---: | :--- | :---: |
| **{P1}** | **US3.1** | As a user, I want to publish posts with food photos, recipe links, and descriptions so that I can share my culinary creations with the community. | **5** |
| **{P1}** | **US3.2** | As a user, I want to edit or delete my existing posts so that I can correct mistakes or remove unwanted content. | **3** |
| **{P1}** | **US3.3** | As a user, I want to like and comment on community posts so that I can engage with other food creators. | **5** |
| **{P2}** | **US3.4** | As a user, I want to bookmark public posts into a "Saved Posts" collection so that I can revisit inspiring ideas later. | **3** |
| **{P2}** | **US3.5** | As a user, I want to follow other users so that their new recipes and posts appear on my home feed. | **3** |

**Sprint 3 Total: 19 Story Points**

---

### Sprint 4: Smart Discovery, Filtering & Planning (Target: 18 pts)
*Focus: Social connection discovery, smart recipe filters, dietary curation, and grocery list utility.*

| Priority | ID | User Story | Points |
| :---: | :---: | :--- | :---: |
| **{P1}** | **US4.1** | As a user, I want to find and connect with friends via username or contact search so that I can build my culinary network. | **5** |
| **{P1}** | **US4.2** | As a user, I want to generate an aggregated grocery checklist from selected recipes so that I know what to purchase at the store. | **5** |
| **{P2}** | **US4.3** | As a user, I want to browse a personalized discovery feed of trending recipes so that I can explore new culinary ideas. | **5** |
| **{P2}** | **US4.4** | As a user, I want to filter recipes by dietary tags (e.g., low-calorie, vegan, gluten-free) and themes (e.g., quick dinner, date night) so that I find meals tailored to my occasion. | **5** |

**Sprint 4 Total: 20 Story Points**

---

## 3. Release Summary

| Sprint | Milestone Focus | Story Points |
| :---: | :--- | :---: |
| **Sprint 1** | Project Setup, User Authentication, Profile Management & Core Recipe Creation | 21 |
| **Sprint 2** | Recipe Categorization, Structured Ingredients, Tools & Search Functionality | 16 |
| **Sprint 3** | Social Feed, Post Authoring/Editing, Likes, Comments, Bookmarks & Follows | 19 |
| **Sprint 4** | Friend Connections, Smart Filtering/Discovery & Automated Grocery List | 20 |
| **Total** | **Release 1.0 Cumulative Workload** | **76 Points** |

---

## 4. Sanity Check & Capacity Analysis

### Team Velocity & Capacity
- **Team Size:** 5 developers (Maximo Mora, Bryan Moreno, Ulises Diaz, John Weaver, Benjamin Ong).
- **Estimated Velocity:** ~18–19 story points per 2-week sprint based on historical course baselines.
- **Total Capacity across 4 Sprints:** $4 \times 18.5 \text{ pts} \approx 74\text{–}76 \text{ story points}$.
- **Total Planned Scope:** 76 story points. The planned release scope aligns within 1–2 points of total capacity.

### Workload Distribution & Risk Factors
1. **Sprint 1 Infrastructure & Spike Allowance:** Sprint 1 includes fundamental setup (Git repositories, CI/CD, linting, shared database schemas, and frontend/backend scaffolding). Although Sprint 1 contains 21 story points on paper, US1.5 (Personal Recipe Tab, 3 pts) has been identified as a stretch goal that can be deferred to Sprint 2 if environment setup incurs unexpected overhead.
2. **Academic Calendar (Midterms & Holidays):** Sprint 2 coincides with university midterm examinations. Accordingly, Sprint 2 has been intentionally scoped to **16 story points** (below the 18-point average) to prevent overcommitment during exam weeks.
3. **Sprint 3 & 4 Social Complexity:** Sprints 3 (19 pts) and 4 (20 pts) rely on established architectural foundations from Sprints 1 and 2. If velocity slows, non-critical {P2} user stories (e.g., US4.3 Discovery Feed or US4.4 Advanced Filters) will be descoped to the product backlog.

---

## 5. Product Backlog (Deferred for Subsequent Releases)

The following stories were evaluated during release planning but deferred to future iterations to maintain MVP delivery discipline:

### Tier 1: Advanced Culinary Utilities & AI Features
| Priority | ID | User Story | Points |
| :---: | :---: | :--- | :---: |
| {P2} | PB-01 | As a user, I want to automatically parse and generate ingredient lists from recipe photos or text using AI so that recipe entry is frictionless. | 8 |
| {P2} | PB-02 | As a user, I want an integrated multi-timer tool so that I can track multiple cooking stages simultaneously. | 2 |
| {P3} | PB-03 | As a user, I want to discover, categorize, and save beverage and cocktail recipes so that I can plan complete meal pairings. | 3 |

### Tier 2: Enhanced Social & Communication Features
| Priority | ID | User Story | Points |
| :---: | :---: | :--- | :---: |
| {P2} | PB-04 | As a user, I want to send direct messages and share recipes privately with friends so that we can coordinate cooking ideas. | 8 |
| {P2} | PB-05 | As a user, I want to receive push and in-app notifications when users interact with my posts or follow me so that I stay engaged. | 5 |
| {P2} | PB-06 | As a user, I want to share posts to external social media platforms (Instagram, Twitter, link copy) so that I can share food content with friends outside the app. | 3 |
| {P2} | PB-07 | As a user, I want to pin selected posts to the top of my profile so that I can showcase my signature dishes. | 2 |
| {P2} | PB-08 | As a user, I want to add audio/music tracks to my recipe video posts so that my content is more engaging. | 5 |
| {P2} | PB-09 | As a user, I want to organize and RSVP to cooking meetups with friends so that we can cook together in person. | 8 |

### Tier 3: Restaurant Discovery & Local Food Community
| Priority | ID | User Story | Points |
| :---: | :---: | :--- | :---: |
| {P2} | PB-10 | As a user, I want to locate nearby restaurants and food markets on an interactive map so that I can discover dining options in my area. | 5 |
| {P2} | PB-11 | As a user, I want to write ratings and reviews for local restaurants so that I can share recommendations with the community. | 5 |
| {P2} | PB-12 | As a user, I want to save favorite restaurants to my profile so that I can quickly access menus and directions. | 3 |
| {P2} | PB-13 | As a user, I want to view other food creators' favorite restaurants and dishes so that I can discover curated local dining spots. | 5 |

### Tier 4: Gamification, Streaks & Smart Recommendation Engine
| Priority | ID | User Story | Points |
| :---: | :---: | :--- | :---: |
| {P3} | PB-14 | As a user, I want to earn culinary badges and achievements for milestone recipes so that I feel rewarded for active cooking. | 5 |
| {P3} | PB-15 | As a user, I want to maintain a weekly cooking streak counter so that I stay motivated to prepare home-cooked meals. | 5 |
| {P3} | PB-16 | As a user, I want an ML-powered recommendation engine based on past likes and search history so that I receive highly relevant recipe suggestions. | 8 |
