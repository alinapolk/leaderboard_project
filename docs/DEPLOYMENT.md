# Deployment Guide

## Server
- Host: 172.12.12.81 (internal TPU network)
- Access via jump host: `ssh -J vag72@main.red.tpu.ru vag72@172.12.12.81`
- OS: Ubuntu 24.04 LTS

## Stack
- Docker Compose (5 services: web, worker, beat, db, redis)
- Network mode: host (due to TPU corporate network restrictions)
- Python 3.13, PostgreSQL 16, Redis 7

## URLs
- Admin: http://172.12.12.81:8000/admin/
- Swagger: http://172.12.12.81:8000/api/schema/swagger-ui/
- API: http://172.12.12.81:8000/api/

## Key commands
```bash
cd ~/leaderboard_project/docker
docker compose ps                    # status
docker compose logs web --tail=50    # logs
docker compose restart web           # restart
docker compose exec web python manage.py sync_all   # resync
docker compose exec web python manage.py reset_data # clean DB
```

## Build notes
- Build requires `--network=host` (TPU blocks Docker bridge NAT)
- After code changes: `docker build --network=host -t leaderboard-app:latest -f docker/Dockerfile ..`

## Backups
- Daily at 03:00 via cron
- Location: ~/leaderboard_backups/
- Retention: 30 days
