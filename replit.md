# 1688 Sourcing Tool

A FastAPI web app for finding likely 1688 source factories, comparing supplier coverage, and exporting sourcing results.

## Run & Operate

- `uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}` — run the FastAPI server
- `python app.py` — run the server using the app's configured host and port
- `pip install -r requirements.txt` — install Python dependencies
- `pytest` — run the test suite
- Demo mode is enabled by default; live provider settings use `PROVIDER_API_KEY`, `PROVIDER_NAME`, `PROVIDER_BASE_URL`, and `DEMO_MODE`

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

_Populate as you build — short repo map plus pointers to the source-of-truth file for DB schema, API contracts, theme files, etc._

## Architecture decisions

_Populate as you build — non-obvious choices a reader couldn't infer from the code (3-5 bullets)._

## Product

_Describe the high-level user-facing capabilities of this app once they exist._

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

_Populate as you build — sharp edges, "always run X before Y" rules._

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
