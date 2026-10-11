---
name: menuopt-project
description: "Use when working on MenuOpt: understand its gastronomic planning platform, FastAPI and Angular architecture, PostgreSQL schema, use cases CU01-CU26, recommendations, reservations, orders, AI assistant, tests, Docker setup, or project-specific implementation decisions."
---

# MenuOpt Project Context

Use this skill when implementing, debugging, testing, documenting, or explaining MenuOpt. It provides the product and architecture context needed to make changes consistent with the existing system.

## Product Goal

MenuOpt is an academic gastronomic-planning platform developed for Ingeniería de Software 1 using Scrum. It helps consumers plan meals around budget, number of people, meal type, location, and preferences; compare restaurant meals with cooking at home; and connect consumers with restaurants for reservations and orders.

The delivered product is a responsive web application. A mobile directory exists, but the final-delivery documentation identifies Flutter/mobile as future scope; do not imply a mobile app is implemented unless the current source tree proves otherwise.

## Current Functional Scope

The repository documents 26 use cases (CU01-CU26), implemented primarily in the web application and API:

- **CU01-CU04 — Accounts and access:** customer registration, JWT login, profile/password management, and administrator user management.
- **CU05-CU08, CU10 — Restaurant catalog:** restaurant registration and management, categories, dishes, dish preferences, and availability (CU09 Gestionar Ingredientes fue eliminado permanentemente a solicitud del usuario).
- **CU11-CU16 — Planning and recommendations:** meal plans, user preferences, recommendations, comparison of restaurant versus home preparation, ingredient requirements, and places to buy ingredients.
- **CU17-CU19 — Restaurant layout:** 2D restaurant areas, normalized-coordinate layouts, table management, and validated symmetric table combinations within an area.
- **CU20-CU22 — Availability and reservations:** date/time/capacity-aware table availability, customer booking and cancellation, and restaurant reservation management.
- **CU23-CU24 — Orders:** customer orders and restaurant kitchen tickets, with historical prices and controlled status transitions.
- **CU25 — Audit:** administrator access to the system event log.
- **CU26 — AI assistant:** natural-language request interpretation and explanations of actual recommendations and comparisons.

For the authoritative endpoint inventory, roles, test accounts, and local URLs, consult [`README.md`](../../../README.md). For detailed requirements, test scenarios, and traceability, consult [`documentacion/PLAN_DE_PRUEBAS.md`](../../../documentacion/PLAN_DE_PRUEBAS.md), [`documentacion/trazabilidad.md`](../../../documentacion/trazabilidad.md), and [`documentacion/ENTREGA_FINAL.md`](../../../documentacion/ENTREGA_FINAL.md). Documentation can lag behind code; inspect the relevant source before asserting current behavior.

## Architecture and Stack

- **Backend:** Python, FastAPI, Pydantic 2, SQLAlchemy, PostgreSQL driver `psycopg`, Alembic migrations, and JWT authentication.
- **Frontend:** Angular 18, standalone components, Signals, Reactive Forms, Angular Router, authentication/role guards, and an HTTP interceptor for JWT. Production serving is configured with Nginx.
- **Database:** PostgreSQL 16 with relational models for users/roles, restaurants, dishes, ingredients, plans/preferences, recommendations, shopping locations, areas/tables, reservations, and orders.
- **Local orchestration:** Docker Compose defines PostgreSQL, backend, and frontend. The Compose ports documented by the project are PostgreSQL 5432, API 8000, and web 4200.
- **AI:** `backend/app/ai` defines an abstract `ProveedorIA` and mock/Gemini implementations. Configuration is environment-based (`AI_ENABLED`, `AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL`, `AI_TIMEOUT_SECONDS`). The mock provider allows use without an external API key.

The usual backend flow is **router → schema validation → service/business rules → repository/SQLAlchemy model → PostgreSQL**. Keep HTTP concerns in routers, request/response contracts in schemas, domain orchestration and rules in services, and persistence queries in repositories, following neighboring code.

## Important Domain Invariants

Preserve these rules when changing related features:

1. **Authorization and ownership:** enforce the permitted role and resource ownership on the server, not only in Angular. Customer plans and recommendations must remain scoped to their owner; restaurant operations must remain scoped to the owning restaurant.
2. **Recommendations are deterministic business logic:** eligibility, preference matching, quantities, cost, budget checks, and scoring belong to the existing recommendation/preparation algorithms. AI may interpret or explain; it must not invent database facts, calculate authoritative prices, or replace the optimizer.
3. **Money and historical order data:** follow the existing `Decimal` handling. Order line prices are snapshots of prices at order time and must not change when the catalog is edited later.
4. **Reservations are time- and concurrency-sensitive:** preserve overlap/capacity checks, transaction boundaries, row locking where used, conflict responses (including HTTP 409), and allowed reservation state transitions.
5. **Orders use a controlled state machine:** preserve the transitions documented in the project (such as `PENDIENTE → ACEPTADO → EN_PREPARACION → LISTO → ENTREGADO`) and existing cancellation/authorization rules.
6. **Restaurant layout relationships:** retain normalized coordinates and same-area, symmetric table-combination validation.
7. **AI is optional and peripheral:** respect the provider abstraction, timeout/configuration behavior, parsing/validation, and safe behavior when a provider is unavailable. Do not expose API keys or send secrets to logs.
8. **Database changes require migrations:** update Alembic revisions for schema changes; do not rely on manual database edits or `create_all` as a substitute for project migrations.

## Repository Map

- `backend/app/routers/` — API route modules, including authentication, users, restaurants, planning, recommendations, reservations, orders, and AI assistance.
- `backend/app/schemas/` — Pydantic request and response models.
- `backend/app/services/` — business logic, algorithms, and use-case orchestration.
- `backend/app/repositories/` — database access.
- `backend/app/models/` — SQLAlchemy entities and relations.
- `backend/app/security/` and `backend/app/core/` — authentication, authorization, ownership, and shared API concerns.
- `backend/app/ai/` — AI provider interface, implementations, prompts, parsing, and assistant schemas.
- `backend/migrations/versions/` — Alembic schema history.
- `backend/tests/` and `backend/test_part*_backend.py` — backend and feature regression tests.
- `frontend-web/src/app/core/` — shared services, routing, guards, and HTTP concerns.
- `frontend-web/src/app/features/` — Angular feature areas corresponding to application workflows.
- `frontend-web/src/app/layouts/` and `shared/` — layouts and reusable UI.
- `documentacion/` — final delivery, test plan, and requirements traceability.
- `database/` and `mobile/` currently contain no substantive implementation in the inspected tree; verify before treating them as implemented modules.

## Development and Validation Workflow

1. Identify the requested use case, role, resource owner, and its existing router/schema/service/repository/model and Angular feature.
2. Read adjacent implementation and the relevant use-case documentation/tests before editing. Treat source and migrations as authoritative when they disagree with narrative documentation.
3. Make the smallest complete change and preserve existing Spanish naming, API contracts, response shapes, error conventions, and UI patterns.
4. For schema changes, add/adjust a migration and verify upgrade behavior. Avoid destructive database operations or modifying unrelated existing data.
5. Add or update focused tests for success paths, validation, authorization/ownership, and relevant state/concurrency edge cases.
6. Run the smallest relevant test/build command first; report any environment limitation accurately rather than claiming an unrun validation passed.
7. Do not commit secrets, credentials, or local `.env` contents. Development defaults and test accounts are for local use only.

Common project commands from the repository root:

```sh
docker compose up -d --build
docker compose ps
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.database.crear_admin
```

The backend OpenAPI UI is at `http://localhost:8000/docs`, the frontend at `http://localhost:4200`, and the database health endpoint at `http://localhost:8000/salud/base-datos`. For focused tests, run the relevant pytest file(s) from `backend`; see the test plan and final-delivery report for the test inventory.

## Scope and Reporting

Do not claim an item is implemented, tested, or deployed based solely on the delivery report. Verify the current source, migrations, tests, and runtime as appropriate. Clearly distinguish:

- existing behavior from requested enhancements;
- web functionality from future mobile scope;
- deterministic recommendation results from AI-generated explanations;
- local development defaults from production-ready secrets/configuration;
- test results that were actually run from historical results stated in documentation.
