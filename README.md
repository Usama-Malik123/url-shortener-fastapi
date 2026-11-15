# URL Shortener

A small, production-style FastAPI URL shortener. This is the **app layer** of a larger DevOps
portfolio project — this same codebase is later deployed via Terraform onto AWS ECS (EC2),
then onto Kubernetes with ArgoCD, and monitored with Prometheus/Grafana. This repo focuses on
getting the application itself right: clean structure, env-driven config, real migrations, and
tests that run against real dependencies.

## Architecture

```
client --> FastAPI --> Redis (cache-aside) --> Postgres
                 \--> /metrics (Prometheus text format)
```

- **Postgres** is the source of truth for shortened URLs, managed by **Alembic** migrations.
- **Redis** caches `code -> target_url` lookups (cache-aside, TTL-based) so repeated redirects
  don't hit Postgres.
- **prometheus-fastapi-instrumentator** exposes request count/latency metrics at `/metrics` for
  future scraping by Prometheus.

## Endpoints

| Method | Path       | Description                                  |
|--------|------------|-----------------------------------------------|
| POST   | `/shorten` | Create a short code for a URL                 |
| GET    | `/{code}`  | Redirect to the original URL (302)            |
| GET    | `/health`  | Liveness/readiness check (Postgres + Redis)   |
| GET    | `/metrics` | Prometheus-format metrics                     |

## Run locally

Requires Docker and Docker Compose.

```bash
cp .env.example .env

# start the databases
docker compose up -d postgres redis

# apply migrations (one-off, not run automatically on container start)
docker compose run --rm app alembic upgrade head

# start the app
docker compose up -d app
```

Try it out:

```bash
curl -X POST localhost:8000/shorten \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'
# {"code":"abc1234","short_url":"http://localhost:8000/abc1234","target_url":"https://example.com/"}

curl -i -L localhost:8000/abc1234
# redirects to https://example.com/

curl localhost:8000/health
curl localhost:8000/metrics
```

## Run tests

Tests run against real Postgres and Redis (no mocking), matching CI.

```bash
docker compose up -d postgres redis

python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

export DATABASE_URL=postgresql+psycopg://urlshortener:urlshortener@localhost:5432/urlshortener
export REDIS_URL=redis://localhost:6379/0

alembic upgrade head
pytest -v
```

## Lint

```bash
ruff check .
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every push and pull request:
- `lint` — `ruff check .`
- `test` — pytest against Postgres + Redis service containers
- `docker-build` — builds the production image

## Project status / roadmap

This repo is step 1 of a multi-phase DevOps portfolio:
1. **This repo** — the FastAPI app, containerized, tested, CI'd.
2. Terraform + AWS ECS (EC2) deployment.
3. Kubernetes + ArgoCD deployment.
4. Prometheus + Grafana observability stack.
