# QA Baseline

Date: 2026-09-28
Environment: Windows / Python 3.12.2 / Node 18+

## Backend
PASS - 27/27 tests pass out of the box using pytest.

## Frontend
PASS - `npm run build` succeeds.
(Note: `npm run lint` failed due to missing eslint dependency, but build passes).

## Build
PASS - Vite builds successfully in 4.9s.

## Tests
PASS - Backend integration tests pass.

## Hindsight
PASS - The system is capable of running in fallback mode out of the box, and tests pass. (Real verification pending).

## LLM
PASS - Configured to mock out of the box for tests.

## Database
PASS - SQLite database seeds properly.

## Demo Mode
PENDING - Needs backend running to verify.
