# RecallDesk QA Final Report

## 1. Executive Summary

RecallDesk has a coherent FastAPI + React/Vite support-agent implementation with explicit Hindsight retain/recall abstractions, customer-scoped memory-bank naming, demo endpoints, tickets, and a database-backed application model. The frontend production build and backend automated suite pass in the available environment. The largest evidence gap is operational rather than a confirmed product failure: a live Hindsight service, live LLM, routed browser preview, and full restart/demo workflow could not be verified in this sandbox.

## 2. Environment

- Date: 2026-09-29
- Backend: FastAPI, Pydantic 2, SQLAlchemy, OpenAI client, Hindsight client
- Frontend: React/Vite/TypeScript
- Runtime: Python 3.13, Node/npm, Linux Vercel Sandbox
- Database test scope: SQLite-backed test setup

## 3. Baseline Results

See `QA_BASELINE.md`. Initial dependency resolution failed on the SQLAlchemy and uvicorn constraints; these were corrected to compatible ranges. The baseline frontend build passed, lint was unavailable, and browser routing was unavailable.

## 4. Tests Executed

- Backend: `python -m pytest -q` → **27 passed, 1 skipped**.
- Frontend: `npm run build` → **PASS**; TypeScript and Vite production build completed.
- Frontend lint: **BLOCKED**; `eslint` executable was not installed.
- Backend import/startup: **BLOCKED in this environment**; uvicorn was not present in the partial targeted environment.
- Browser: attempted Vite preview verification; agent-browser was routed to `localhost:3000` and returned `404 SANDBOX_NOT_FOUND` while Vite reported port 5174.

## 5. Hindsight Verification

Static/code-level verification found:

- `HindsightManager.retain()` and `HindsightManager.recall()` paths.
- Customer-specific bank identifiers are derived from customer IDs.
- Memory status and explicit retain/recall API routes exist.
- Support-agent processing includes recall before response and retain after processing.

A live RETAIN → PERSIST → RECALL round trip was **not verified** because no reachable Hindsight service was available. Therefore this report does not claim production Hindsight operation.

## 6. Memory Learning Verification

The repository contains tests covering memory integration behavior, and the suite passed. Live behavior-change verification for successful billing resolution, failed troubleshooting, and post-restart recall was **not completed**. The implementation appears designed for this lifecycle, but external-service evidence is still required.

## 7. Customer Isolation Verification

Code inspection found customer-scoped memory-bank naming and customer IDs passed through memory operations. Automated tests passed, but a live two-customer Hindsight isolation experiment was **not completed**. This should be a release gate before judging the product as production-ready.

## 8. LLM Verification

The OpenAI client and graceful error handling paths are present. No live request, invalid-key request, timeout, rate-limit, or malformed-response integration test was run because live provider configuration was unavailable. No secret was exposed in the test output.

## 9. Backend Verification

- FastAPI route modules are present for chat, customers, memory, tickets, knowledge, and demo functionality.
- Automated suite: **27 passed, 1 skipped**.
- API contract and validation paths covered by the existing tests passed.
- Startup command could not be fully exercised because uvicorn was absent from the targeted environment setup.

## 10. Frontend Verification

- TypeScript compilation and Vite production build passed.
- Vite dev server started on port 5174.
- Browser dashboard/chat/profile/memory/ticket interaction verification was blocked by preview routing (`404 SANDBOX_NOT_FOUND` on agent-browser localhost route).
- Lint was blocked because the `eslint` binary was unavailable.

## 11. Database Verification

The automated suite exercised the SQLite application database paths successfully. Static inspection found customer, ticket, chat, and knowledge routes. A full create/read/update/delete and restart persistence run against a running backend was not completed.

## 12. Security Review

- No committed API key was found during the inspected configuration/code path.
- Hindsight memory is customer-scoped by bank identifier in the manager.
- Global exception handling logs server-side details rather than returning raw tracebacks.
- Live authorization, cross-customer isolation, prompt-injection resistance, and production CORS behavior require a deployed/integrated verification pass.

## 13. Bugs Found

### Medium — dependency constraints prevent clean installation
- **File:** `backend/requirements.txt`
- **Problem:** SQLAlchemy constraint was incompatible with `hindsight-api-slim==0.10.1`.
- **Reproduction:** Installing requirements produced a resolver conflict requiring SQLAlchemy >=2.0.44.
- **Fix:** Changed to `sqlalchemy<2.1,>=2.0.44`.
- **Verification:** Targeted environment installed SQLAlchemy 2.0.54 and the backend test suite passed.

### Medium — uvicorn constraint was incompatible with current FastAPI resolution
- **File:** `backend/requirements.txt`
- **Problem:** The pinned uvicorn version could not satisfy the resolved FastAPI stack.
- **Reproduction:** Requirements installation reported the uvicorn conflict.
- **Fix:** Changed to `uvicorn[standard]>=0.38.0,<1`.
- **Verification:** Constraint is compatible with the resolved package metadata; complete install remained slow because Hindsight's optional all-dependency graph is large.

### Low — frontend lint command is not runnable in the current install
- **File:** `frontend/package.json` / installed dependency state
- **Problem:** `npm run lint` invokes `eslint`, but the executable was unavailable.
- **Reproduction:** `npm run lint` returned `eslint: command not found`.
- **Fix:** No code change made; dependency installation state must be repaired separately.
- **Verification:** Not verified.

### Low — async test is skipped
- **File:** `backend/tests/test_memory_integration.py`
- **Problem:** Pytest reported an async test skipped despite pytest-asyncio being listed, indicating an environment/configuration mismatch.
- **Reproduction:** Test run reported `27 passed, 1 skipped` and `PytestUnhandledCoroutineWarning`.
- **Fix:** No test rewrite made without inspecting the intended test semantics further.
- **Verification:** Outstanding.

## 14. Tests Added

No new application tests were added. Existing tests were executed; changes were limited to dependency compatibility and QA evidence files.

## 15. Tests Passed

- Backend automated suite: 27 passed.
- Frontend TypeScript compilation.
- Frontend Vite production build.

## 16. Tests Failed or Blocked

- Live Hindsight round trip.
- Live LLM failure and success scenarios.
- Browser UI workflow due sandbox preview routing.
- Backend uvicorn startup in the partial environment.
- Frontend lint due missing eslint executable.
- One async test skipped.
- Full restart persistence experiment.

## 17. Remaining Issues

1. Verify the complete Hindsight RETAIN → PERSIST → RECALL flow against a reachable service.
2. Run two-customer isolation and no-memory experiments with real bank data.
3. Add/fix frontend lint dependencies and run lint.
4. Correct the skipped async test/configuration.
5. Run live LLM success/error tests without exposing provider secrets.
6. Validate the full demo in a routable browser preview or deployed preview.

## 18. Hackathon Readiness

### Innovation
The product has a clear memory-first customer-support thesis and exposes memory status/timeline concepts rather than treating memory as invisible plumbing. Live judge evidence is still needed.

### Hindsight Memory
The implementation has explicit retain/recall integration points and customer-scoped banks. The critical live persistence and behavior-change proof is currently missing, so this is the biggest readiness gap.

### Technical Implementation
The architecture is separated into API routes, agents, memory manager, database models, and a typed frontend. Automated backend tests and frontend build pass. Dependency installation and startup reproducibility need tightening.

### User Experience
The frontend is buildable and has dashboard-oriented service layers for customer, chat, memory, tickets, and demo views. Interactive UX could not be judged because browser routing failed in the sandbox.

### Real-world Impact
The workflow maps to a credible support use case: remembering successful and failed troubleshooting reduces repeated work. A reliable live demo and isolation evidence are required to substantiate the claim.

## 19. Final Demo Sequence

1. Start the backend with a reachable Hindsight service and configured LLM provider.
2. Open the RecallDesk frontend and select Sarah Mitchell / Vertex Labs.
3. Send: “My payment failed when I tried upgrading my plan.”
4. Confirm the billing-profile update resolved it: “Updating my billing profile fixed it. Thanks.”
5. Show the retained memory/timeline entry.
6. Start a later session and send: “I’m having another billing problem.”
7. Show the recalled successful billing context and personalized response.
8. Repeat with a failed reconnect-integration attempt and confirm the agent avoids blindly repeating it.
9. Switch to a second customer and demonstrate that the first customer’s memory is absent.
10. Show the demo stats, memory status, and escalation handoff with prior attempts included.
