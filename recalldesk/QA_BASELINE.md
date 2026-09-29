# QA Baseline

Date: 2026-09-29
Environment: Linux Vercel Sandbox; Python 3.13; Node/npm; backend dependency installation initially blocked by incompatible pins.

## Backend
FAIL — initial startup attempt could not launch because the required `uvicorn` executable was not installed in the partial test environment. The application import/test path was later made executable with targeted dependencies.

## Frontend
PASS — Vite development server started on port 5174 (port 5173 was already occupied).

## Build
PASS — `npm run build` completed: TypeScript compiled and Vite produced `dist/`.

## Tests
PASS with warning — after targeted dependency setup, 27 tests passed and 1 async test was skipped. Pytest reported a pytest-asyncio configuration warning.

## Lint
FAIL — `npm run lint` could not run because the local `eslint` executable was unavailable in the frontend install.

## TypeScript
PASS — included in the frontend production build (`tsc`).

## Hindsight
NOT VERIFIED — no live Hindsight service was available in the sandbox. The code contains retain/recall paths and mocked test coverage, but a running external Hindsight round trip was not established.

## LLM
NOT VERIFIED — no live model request was made. The LLM client is present, but no usable live provider configuration was available for a safe integration test.

## Database
PASS for test scope — the backend test suite exercised the SQLite-backed application paths. A separate startup health check was blocked by the missing `uvicorn` installation in the first environment.

## Demo Mode
NOT VERIFIED — the browser preview could not be routed by `agent-browser`; it returned `404 SANDBOX_NOT_FOUND` on localhost:3000 despite Vite reporting localhost:5174.

## Initial Findings
- `requirements.txt` pinned SQLAlchemy below the minimum required by `hindsight-api-slim==0.10.1`.
- `requirements.txt` pinned an older uvicorn that was incompatible with the current FastAPI dependency resolution.
- Frontend lint tooling was not available in the installed node modules.
- Live Hindsight, LLM, restart persistence, and browser workflow evidence remain unconfirmed.
