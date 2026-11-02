## Установка и запуск через Docker

### Системные требования

| Параметр | Минимум | Рекомендуется |
|----------|---------|---------------|
| **ОС** | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |
| **CPU** | 2 ядра | 4 ядра |
| **RAM** | 4 GB | 8 GB |
| **Диск** | 20 GB | 50 GB SSD |
| **Порты** | 80, 443, 8000 | + 5432 (PostgreSQL), 6379 (Redis) |

---

### Шаг 1: Установка Docker на Ubuntu 24

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y ca-certificates curl gnupg lsb-release git

# Добавление официального GPG ключа Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Добавление репозитория Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Добавление текущего пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER

# Применение изменений (перелогиниться или выполнить)
newgrp docker

# Проверка установки
docker --version
docker compose version
```

**Проверка:**
```bash
docker run hello-world
```

Должно вывести `Hello from Docker!`

---

### Шаг 2: Клонирование проекта

```bash
# Переход в рабочую директорию
cd /opt  # или /home/ubuntu, или другая удобная папка

# Клонирование репозитория
git clone https://github.com/YOUR_USERNAME/LeaderBoardTPU_Project.git
cd LeaderBoardTPU_Project

# Переключение на нужную ветку (если требуется)
git checkout main
```

---

### Шаг 3: Настройка окружения

```bash
# Переход в папку docker
cd docker

# Создание .env файла из шаблона
cp .env.docker.example .env.docker

# Редактирование .env.docker
nano .env.docker  # или vim, или любой другой редактор
```

**Обязательные изменения в `.env.docker`:**

```env
# Django
SECRET_KEY=<сгенерировать_новый_ключ>
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com,your-server-ip

# Database (можно оставить как есть)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=leaderBoard
DB_USER=postgres
DB_PASSWORD=<сильный_пароль>
DB_HOST=db
DB_PORT=5432

# API Витрины и ТПУ
TPU_API_BASE_URL=https://tpu.community.design/dev/api
VITRINA_API_BASE_URL=https://tpu.community.design/dev/api
TPU_API_MOCK_MODE=False
VITRINA_API_MOCK_MODE=False

# Redis
REDIS_CACHE_HOST=redis
```

**Генерация SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Или онлайн: https://djecrety.ir/

---

### Шаг 4: Первый запуск

```bash
# Сборка образов и запуск контейнеров
docker compose up -d --build

# Проверка статуса
docker compose ps
```

**Ожидаемый результат:**
```
NAME                 STATUS
leaderboard_web      Up
leaderboard_worker   Up
leaderboard_beat     Up
leaderboard_db       Up (healthy)
leaderboard_redis    Up (healthy)
```

**Просмотр логов:**
```bash
# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f web
```

---

### Шаг 5: Применение миграций и создание администратора

```bash
# Применение миграций базы данных
docker compose exec web python manage.py migrate

# Сбор статических файлов (для production)
docker compose exec web python manage.py collectstatic --noinput

# Создание суперпользователя
docker compose exec web python manage.py createsuperuser
```

Команда попросит ввести:
- **Username:** `admin` (или другой)
- **Email:** `admin@example.com`
- **Password:** (сильный пароль, при вводе не отображается)

---

### Шаг 6: Первоначальная синхронизация данных

```bash
# Очистка тестовых данных (если есть)
docker compose exec web python manage.py reset_data

# Синхронизация с реальными API
docker compose exec web python manage.py sync_all

# Очистка Redis кеша
docker compose exec redis redis-cli -n 1 FLUSHDB
```

**Ожидаемый результат:**
```
✅ Синхронизация завершена:
  projects: {'received': 9, 'created': 9, 'updated': 0, 'failed': 0}
  team_members: {'received': 6, 'created': 6, 'updated': 0, 'failed': 0}
```

---

### Шаг 7: Проверка работы

**Открой в браузере:**

| URL | Описание |
|-----|----------|
| `http://your-server-ip:8000/` | Главная страница |
| `http://your-server-ip:8000/admin/` | Админка Django |
| `http://your-server-ip:8000/api/schema/swagger-ui/` | Swagger UI документация |

**Проверка через shell:**
```bash
docker compose exec web python manage.py shell
```

```python
from LeaderBoard.models import Projects, Students, Student_Teams

print(f"Проектов: {Projects.objects.count()}")
print(f"Студентов: {Students.objects.count()}")
print(f"Участников: {Student_Teams.objects.count()}")
exit()
```

---

### Шаг 8: Настройка firewall (UFW)

```bash
# Включение UFW (если не включен)
sudo ufw enable

# Разрешение SSH (ОБЯЗАТЕЛЬНО!)
sudo ufw allow 22/tcp

# Разрешение HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Разрешение Django (для разработки)
sudo ufw allow 8000/tcp

# Проверка статуса
sudo ufw status
```

---

## Управление проектом

### Основные команды

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Перезапуск
docker compose restart

# Пересборка после изменений кода
docker compose up -d --build

# Просмотр логов
docker compose logs -f web
docker compose logs --tail=50 worker
```

### Обновление проекта

```bash
# Перейти в папку проекта
cd /opt/LeaderBoardTPU_Project

# Получить последние изменения
git pull origin main

# Пересобрать и перезапустить
docker compose down
docker compose up -d --build

# Применить новые миграции
docker compose exec web python manage.py migrate

# Собрать статические файлы
docker compose exec web python manage.py collectstatic --noinput
```

### Резервное копирование базы данных

```bash
# Создание бэкапа
docker compose exec db pg_dump -U postgres leaderBoard > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
cat backup_20261028_120000.sql | docker compose exec -T db psql -U postgres leaderBoard
```

### Очистка и пересоздание

```bash
# Полная очистка (ВНИМАНИЕ: удалит все данные!)
docker compose down -v
docker system prune -a

# Запуск с нуля
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py sync_all
```

---

## Полезные команды

### Django shell
```bash
docker compose exec web python manage.py shell
```

### Просмотр всех management команд
```bash
docker compose exec web python manage.py help
```

### Синхронизация данных
```bash
# Полная синхронизация
docker compose exec web python manage.py sync_all

# Только Витрина
docker compose exec web python manage.py sync_all --source vitrina
```

### Работа с кешем Redis
```bash
# Войти в Redis CLI
docker compose exec redis redis-cli -n 1

# Посмотреть все ключи
KEYS *

# Очистить кеш
FLUSHDB

# Выйти
exit
```

### Просмотр базы данных
```bash
# Войти в PostgreSQL
docker compose exec db psql -U postgres leaderBoard

# Список таблиц
\dt

# Выйти
\q
```

---

## Troubleshooting

### Проблема: Порт 8000 уже занят
```bash
# Найти процесс
sudo lsof -i :8000

# Убить процесс
sudo kill -9 <PID>
```

### Проблема: Контейнер не запускается
```bash
# Посмотреть логи
docker compose logs web --tail=50

# Проверить статус
docker compose ps

# Перезапустить
docker compose restart web
```

### Проблема: Ошибка подключения к базе данных
```bash
# Проверить, что db контейнер healthy
docker compose ps db

# Перезапустить db
docker compose restart db

# Проверить логи
docker compose logs db
```

### Проблема: Миграции не применяются
```bash
# Показать статус миграций
docker compose exec web python manage.py showmigrations

# Применить принудительно
docker compose exec web python manage.py migrate --run-syncdb
```

---