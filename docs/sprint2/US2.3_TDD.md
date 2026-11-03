# US2.3 cooking-log behavior: red phase

The first test-only increment lives on `Ulises`. Production UI/API code is unchanged.

`frontend/src/test/cooking-log.test.tsx` specifies:

- Authenticated users open an accessible "I Cooked This" dialog; Cancel sends no request.
- Notes and rating are optional. A successful authenticated POST to `/api/v1/recipes/{id}/complete` closes the dialog and announces success.
- Notes and a five-star rating are sent using the documented completion payload.
- Server errors retain notes and allow retry.
- While saving, duplicate clicks send only one request.
- Signed-out visitors cannot submit a cooking log.

The dialog, Notes field, star radio controls, Cancel and Save cooking log buttons are proposed accessible UI labels for the implementation step.

## Expected results before implementation

Run `npm test` from frontend. Five new tests intentionally fail at the missing cooking-log action. The signed-out test and all 14 existing frontend tests pass (15 passing, 5 failing overall). The production build still passes. Do not skip tests or mark them expected failures: they should turn green when implementation lands. CI frontend tests will remain red during this intermediate commit.

The HTTP layer is mocked here. These tests do not establish backend persistence, authorization, rating validation, or the server's 60-second duplicate protection; those need integration tests with the backend slice.

Custom cooked-date submission is deferred because the approved LogCookedRequest currently defines only notes and rating despite mentioning a date picker elsewhere. Cooking-history tab behavior belongs to a later increment.
