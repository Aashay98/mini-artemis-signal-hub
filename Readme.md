# Mini-Artemis Signal Hub

## Local Dev (Docker Compose)

```bash cp .env.example .env  # Set DB and Redis URLs
docker-compose up --build
```

- API: http://localhost:8000/docs (Swagger UI)
- WebSocket: ws://localhost:8000/ws/signals
- Flower: http://localhost:5555

Migrations
```bash
docker-compose exec api alembic upgrade head
```

Testing
```bash
docker-compose exec api pytest --cov=app
```

## CI/CD
- Lint: ruff, mypy
- Test: pytest (with ≥80% coverage)
- Build: Docker multi-stage
- Push: GitHub Container Registry (GHCR)

See .github/workflows/ci.yml

## Design & Trade-Offs
- Stateless API: All state in DB/Redis. Scales horizontally.
- Redis pub/sub: Simple, low-latency live updates.
- Async pipeline: Celery is decoupled; failures in processing do not block ingestion.
- Partitioned ticks table: Handles large market data volumes.
- Secrets: Use .env for local, AWS Secrets Manager/SSM for prod.
- Observability: Prometheus metrics, Flower UI for Celery.

## Deployment
```bash 
cd infra
terraform init
terraform apply
```

## Time log
| Date       | Task                                | Hours |
| ---------- | ----------------------------------- | ----- |
| 2025-07-14 | Project scaffold, FastAPI setup     | 1     |
| 2025-07-15 | Celery, DB, Redis, endpoints        | 3     |
| 2025-07-16 | Docker, Compose, testing, endpoints | 3     |
| 2025-07-17 | docs, testing, CI/CD, AWS Terraform | 3     |
| **Total**  |                                     | **10** |
