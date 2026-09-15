# Архитектура проекта

LeaderBoardTPU_Project/
├── LeaderBoardTPU_Project/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
│
├── LeaderBoard/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   ├── auth.py
│   │   ├── students.py
│   │   ├── projects.py
│   │   ├── teams.py
│   │   ├── activity.py
│   │   ├── leaderboard.py
│   │   └── meta.py
│   │
│   ├── selectors/
│   │   ├── __init__.py
│   │   ├── student_selectors.py
│   │   ├── project_selectors.py
│   │   ├── team_selectors.py
│   │   └── leaderboard_selectors.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── consent_service.py
│   │   ├── student_service.py
│   │   └── sync_service.py
│   │
│   ├── rating/
│   │   ├── __init__.py
│   │   ├── calculator.py
│   │   ├── service.py
│   │   ├── constants.py
│   │   └── snapshots.py
│   │
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── base_client.py
│   │   ├── tpu/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   ├── dto.py
│   │   │   ├── mapper.py
│   │   │   └── exceptions.py
│   │   └── vitrina/
│   │       ├── __init__.py
│   │       ├── client.py
│   │       ├── dto.py
│   │       ├── mapper.py
│   │       └── exceptions.py
│   │
│   ├── common/
│   │   ├── __init__.py
│   │   ├── pagination.py
│   │   ├── exceptions.py
│   │   ├── permissions.py
│   │   └── throttling.py
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── sync_tasks.py
│   │   ├── rating_tasks.py
│   │   └── maintenance_tasks.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── student.py
│   │   ├── project.py
│   │   ├── team.py
│   │   ├── activity.py
│   │   ├── medal.py
│   │   ├── consent.py
│   │   ├── sync.py
│   │   └── rating_snapshot.py
│   │
│   ├── serializers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── students.py
│   │   ├── projects.py
│   │   ├── teams.py
│   │   ├── activity.py
│   │   ├── medals.py
│   │   ├── leaderboard.py
│   │   └── sync.py
│   │
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── students.py
│   │   ├── projects.py
│   │   ├── teams.py
│   │   ├── rating.py
│   │   ├── sync.py
│   │   └── consents.py
│   │
│   ├── management/
│   │   └── commands/
│   │       ├── fill_test_data_300.py
│   │       └── fill_test_data_2000.py
│   │
│   ├── migrations/
│   ├── apps.py
│   └── urls.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_SPECIFICATION.md
│   ├── RUNBOOK.md
│   ├── request-tpu-data.json
│   └── request-vitrina-data.json
│
├── mocks/
│   ├── tpu-api-mock.json
│   └── vitrina-api-mock.json
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── factories.py
│   ├── test_rating_calculator.py
│   ├── test_leaderboard_api.py
│   ├── test_auth_api.py
│   └── test_sync_mappers.py
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── entrypoint.sh
│
├── .env
├── .env.example
├── .env.docker.example
├── requirements.txt
└── manage.py
