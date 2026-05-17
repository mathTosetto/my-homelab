# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package Management & Environment

- Python 3.14+ required; use `uv` for all package operations
- Install dependencies: `uv sync`
- Run tasks: `uv run inv <task>`
- Activate venv if needed: `source .venv/bin/activate`

## Common Commands

```bash
# Start services
uv run inv up --all              # start all services
uv run inv up --nextcloud        # start specific service
uv run inv up --calibre
uv run inv up --npm
uv run inv up --pi-hole
uv run inv up --immich
uv run inv up --gitea
uv run inv up --uptime-kuma
uv run inv up --portainer
uv run inv up --dashboard
uv run inv up --dashboard --build  # rebuild image before starting (use after code changes)

# Stop services
uv run inv down --all

# Inspect
uv run inv status           # check running containers
uv run inv logs --service nextcloud  # tail logs for a service

# Nextcloud file sync
uv run inv scan

# Project setup (first time)
uv run inv setup
```

## Linting & Formatting

```bash
uv run ruff check .         # lint
uv run ruff format .        # format
pre-commit run --all-files  # run all pre-commit hooks
```

No test suite is configured.

## Architecture

This is a **self-hosted homelab** — a collection of Docker Compose services managed by a Python [Invoke](https://www.pyinvoke.org/) task runner (`tasks.py`).

### Services (`services/`)

Each subdirectory is an independent service with its own `docker-compose.yaml`:

| Service | Port(s) | Purpose |
|---|---|---|
| `nextcloud` | 8080 | Private cloud storage (MariaDB + Redis backend) |
| `calibre-web` | 8083 | eBook library (Hardcover metadata integration) |
| `npm` | 80, 81, 443 | Nginx Proxy Manager — reverse proxy & SSL |
| `pi_hole` | 53, 8081 | DNS-based ad blocking |
| `immich` | 2283 | Photo & video library |
| `gitea` | 3000 | Self-hosted Git service |
| `uptime-kuma` | 3001 | Service uptime monitoring |
| `portainer` | 9000 | Docker container management UI |
| `dashboard` | 8888 | Home screen with service links and health status (locally built image) |

All services share the external Docker network `homelab_network`. Data is persisted in `./data/` subdirectories and an external USB drive at `/Volumes/Elements/homelab/`.

### tasks.py

Central automation entry point. Key internals:
- `SERVICES` dict maps CLI flag names → service folder paths
- `ensure_network()` creates `homelab_network` before any `up`
- `run_compose()` is the low-level wrapper that shells out to `docker compose`
- `up --build` passes `--build` to `docker compose up -d` — required after changing locally built services (e.g. `dashboard`)
- Service startup order follows insertion order of `SERVICES` dict (reversed on `down`)

### Environment Variables

Copy `.env.template` to `.env` and fill in values. Required variables:

- `MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER` — Nextcloud MariaDB credentials
- `HARDCOVER_TOKEN` — JWT for Calibre-Web metadata API

`.gitignore` whitelists only `docker-compose.yaml` files under `services/`; all `data/` directories are excluded.
