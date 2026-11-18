---
id: US3.2.2
story: US3.2
sprint: 3
assignee: Ulises Diaz
estimate_hours: 3
---

# Author-only post actions and deletion confirmation

This is the next sequential task authorized in chat, not an individual assignment inferred from the plan. The plan explicitly assigns Ulises Task 3.2.1; ownership of this follow-on task should be coordinated with the team. GitHub issue #45 describes this UI but its title incorrectly says US3.3.2.

## Component contract

`PostActions` accepts postId, authorId, currentUserId (null for visitors), onEdit(postId) and onDeleted(postId).

- Only matching author/viewer IDs show actions; the backend remains the security boundary.
- Edit closes the dropdown and invokes the parent callback. Editing-modal content remains Task 3.2.3.
- Delete opens a named confirmation dialog, initially focused on Cancel. Cancel and Escape send no request. Tab stays within the dialog.
- Confirm sends an authenticated DELETE via the shared client. Disable controls while pending and guard duplicate clicks immediately.
- Failed requests retain confirmation, show the API error, and allow retry. Only server success invokes onDeleted, allowing the host to remove its card.
- Closing restores trigger focus; requests finishing after unmount cannot update a different page.

## TDD and integration status

With an empty component stub, the initial tests produced 6 expected failures and 2 passing visibility checks. The implementation makes those behaviors pass; an additional test covers outside-click/Escape dropdown dismissal.

This is a reusable component, not yet wired into a production feed. Current main has no post/feed card to host it; the feed implementation is in PR #40. On integration, pass authenticated user identity from the auth provider, use onEdit to open Task 3.2.3's modal, and use onDeleted to remove the card. No placeholder page or duplicate feed was introduced.
