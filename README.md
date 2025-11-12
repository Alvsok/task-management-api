# Task Management API

A comprehensive RESTful API for task management built with Django REST Framework, featuring JWT authentication, PostgreSQL 18 database, advanced filtering, and Docker deployment.

## 🚀 Features

- **Authentication & Authorization**
  - JWT-based authentication with djangorestframework-simplejwt 5.5.1
  - Security through action-based queryset filtering (no separate Permission classes)
  - Users can only view tasks assigned to them or created by them
  - Secure architecture: returns 404 instead of 403 to avoid revealing object existence

- **Task Management**
  - Full CRUD operations (Create, Read, Update, Delete)
  - Task statuses with state machine validation: New → In Progress → Review → Done
  - Status transition rules enforced:
    - Cannot go directly from NEW to DONE
    - Cannot return from DONE to NEW
  - Assign tasks to users
  - Set deadlines (with validation - cannot be in the past)
  - Advanced filtering by status, assignee, creator, deadline range
  - Full-text search in title and description
  - Ordering by any field

- **Comments System**
  - Comment on tasks (creator and assignee only)
  - Edit and delete own comments
  - Author-based permissions

- **API Documentation**
  - OpenAPI 3.0 schema via drf-spectacular
  - Interactive Swagger UI
  - ReDoc documentation
  - Fully documented endpoints with examples

- **Performance Optimization**
  - N+1 query prevention using select_related(), prefetch_related(), annotate()
  - Database indexes on frequently queried fields
  - Optimized admin interface

- **API Versioning**
  - Version prefix: /api/v1/
  - Future-proof architecture for v2 without breaking v1

## 🛠️ Tech Stack

- **Backend**: Django 5.2.8, Django REST Framework 3.16.1
- **Database**: PostgreSQL 18.0 (Alpine)
- **Authentication**: djangorestframework-simplejwt 5.5.1
- **API Documentation**: drf-spectacular 0.29.0 (OpenAPI 3.0)
- **Filtering**: django-filter 25.2
- **Environment Config**: python-decouple 3.8
- **Deployment**: Docker, Docker Compose
- **Python**: 3.12

## 📋 Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Git

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone git@github.com:Alvsok/task-management-api.git
cd task-management-api
```

### 2. Configure environment variables

The `.env.example` file is provided. Create your own `.env`:

```bash
cp .env.example .env
```

**`.env` contents:**
```env
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production-98asd7f89asdf7
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DB_NAME=task_management
DB_USER=taskuser
DB_PASSWORD=taskpass123
DB_HOST=db
DB_PORT=5432
```

**Important**: All database variables use `DB_*` prefix. Docker Compose automatically maps them to `POSTGRES_*` for the database container.

### 3. Build and start containers

```bash
# Build and start all services
docker compose up -d --build

# Check logs
docker compose logs -f web
```

The Django application will automatically start with `python manage.py runserver 0.0.0.0:8000` and be accessible at http://localhost:8000

### 4. Apply migrations

```bash
docker compose exec web python manage.py migrate
```

### 5. Create test data (optional but recommended)

```bash
docker compose exec web python manage.py create_test_data
```

This creates:
- 3 test users (admin, user1, user2)
- 3 sample tasks with different statuses
- 4 comments on tasks

The command is idempotent - you can run it multiple times safely without creating duplicates.

### 6. Access the application

- **API Base URL**: http://localhost:8000/api/v1/
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Django Admin**: http://localhost:8000/admin/

## 🔐 Authentication

All API endpoints (except token endpoints) require JWT authentication.

### Obtain JWT Token

```bash
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

### Use Token in Requests

```bash
curl -X GET http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test Users

After running `create_test_data` command:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| admin | admin123 | Superuser | Full access to admin panel |
| user1 | user123 | Regular user | Has assigned tasks |
| user2 | user123 | Regular user | Has assigned tasks |

## 📚 API Endpoints

**Base URL**: http://localhost:8000/api/v1/

### Authentication Endpoints
- `POST /api/v1/token/` - Obtain JWT token pair (access + refresh)
- `POST /api/v1/token/refresh/` - Refresh access token

### Task Endpoints
- `GET /api/v1/tasks/` - List all accessible tasks (creator or assignee)
- `POST /api/v1/tasks/` - Create a new task
- `GET /api/v1/tasks/{id}/` - Retrieve task details
- `PUT /api/v1/tasks/{id}/` - Full update task (creator only)
- `PATCH /api/v1/tasks/{id}/` - Partial update task (creator only)
- `DELETE /api/v1/tasks/{id}/` - Delete task (creator only)
- `POST /api/v1/tasks/{id}/complete/` - Mark task as done (creator only)

### Comment Endpoints
- `GET /api/v1/comments/` - List all accessible comments
- `POST /api/v1/comments/` - Create a comment (creator or assignee of task)
- `GET /api/v1/comments/{id}/` - Retrieve comment details
- `PUT /api/v1/comments/{id}/` - Full update comment (author only)
- `PATCH /api/v1/comments/{id}/` - Partial update comment (author only)
- `DELETE /api/v1/comments/{id}/` - Delete comment (author only)

## 📖 API Usage Examples

### Create a Task

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement new feature",
    "description": "Add user profile functionality",
    "assignee_id": 2,
    "deadline": "2025-12-31T23:59:59Z"
  }'
```

### List Tasks with Filters

```bash
# Filter by status
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/tasks/?status=in_progress"

# Filter by assignee
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/tasks/?assignee=2"

# Search in title/description
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/tasks/?search=API"

# Order by deadline
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/tasks/?ordering=deadline"
```

### Update Task Status

```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

### Complete Task

```bash
curl -X POST http://localhost:8000/api/v1/tasks/1/complete/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create a Comment

```bash
curl -X POST http://localhost:8000/api/v1/comments/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task": 1,
    "text": "Great progress on this task!"
  }'
```

## 🔍 Filtering & Search

### Task Filtering Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | String | Filter by task status | `?status=done` |
| `assignee` | Integer | Filter by assignee user ID | `?assignee=2` |
| `creator` | Integer | Filter by creator user ID | `?creator=1` |
| `deadline_from` | DateTime | Tasks with deadline after this date | `?deadline_from=2025-01-01T00:00:00Z` |
| `deadline_to` | DateTime | Tasks with deadline before this date | `?deadline_to=2025-12-31T23:59:59Z` |
| `search` | String | Full-text search in title and description | `?search=API` |
| `ordering` | String | Order results by field (prefix with `-` for descending) | `?ordering=-created_at` |

### Task Status Values

- `new` - Newly created task
- `in_progress` - Task is being worked on
- `review` - Task is under review
- `done` - Task is completed

### Example: Complex Query

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/tasks/?status=in_progress&assignee=2&ordering=-deadline"
```

## 🔒 Security Architecture

### Permission Strategy

This project uses **action-based queryset filtering** instead of separate Permission classes. This approach provides:

- **Single source of truth**: All security logic in ViewSet's `get_queryset()` method
- **Simpler code**: No need for separate permission files
- **Better security**: Returns 404 instead of 403, avoiding information disclosure about object existence
- **Maintainability**: All logic in one place

### Task Security Rules

**Implementation in `tasks/views.py:TaskViewSet.get_queryset()`:**

```python
def get_queryset(self):
    user = self.request.user
    # Base: user can see tasks where they are creator OR assignee
    qs = Task.objects.filter(Q(assignee=user) | Q(creator=user))

    # Only creator can update/delete
    if self.action in ['update', 'partial_update', 'destroy']:
        qs = qs.filter(creator=user)

    return qs.select_related('creator', 'assignee') \
             .prefetch_related('comments') \
             .annotate(comments_count=Count('comments'))
```

**What this means:**
- **View (GET)**: Creator OR Assignee can view task
- **Create (POST)**: Any authenticated user can create tasks
- **Update (PUT/PATCH)**: Only Creator (assignee gets 404)
- **Delete**: Only Creator (assignee gets 404)
- **Complete**: Only Creator (explicit check in action method - assignee gets 403)

### Comment Security Rules

**Implementation in `tasks/views.py:CommentViewSet.get_queryset()`:**

```python
def get_queryset(self):
    user = self.request.user
    # User can see comments on tasks they have access to
    qs = Comment.objects.filter(
        Q(task__assignee=user) | Q(task__creator=user)
    )

    # Only author can update/delete
    if self.action in ['update', 'partial_update', 'destroy']:
        qs = qs.filter(author=user)

    return qs.select_related('task', 'author')
```

**What this means:**
- **View**: Users with access to the task (creator or assignee)
- **Create**: Users with access to the task
- **Update/Delete**: Only comment author (others get 404)

### Validation Rules

#### Status Transition Validation
Implemented in `tasks/serializers.py:TaskSerializer.validate_status()`:

- ❌ **Cannot go directly from NEW to DONE** (must pass through IN_PROGRESS or REVIEW)
- ❌ **Cannot return from DONE to NEW** (completed tasks stay completed)
- ✅ Valid transitions: NEW → IN_PROGRESS → REVIEW → DONE

#### Deadline Validation
Implemented in `tasks/serializers.py:TaskSerializer.validate_deadline()`:

- ❌ **Cannot set deadline in the past**
- ✅ Deadline must be a future datetime

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
docker compose exec web python manage.py test

# Run with verbose output
docker compose exec web python manage.py test -v 2

# Run specific test class
docker compose exec web python manage.py test tasks.tests.TaskAPITest

# Run with coverage
docker compose exec web coverage run --source='.' manage.py test
docker compose exec web coverage report
```

### Test Coverage

The project includes 20+ comprehensive unit tests covering:

- ✅ Task CRUD operations
- ✅ Comment CRUD operations
- ✅ Authentication (authenticated vs unauthenticated)
- ✅ Authorization (creator vs assignee permissions)
- ✅ Status transition validation
- ✅ Deadline validation
- ✅ Complete action (creator can, assignee cannot)
- ✅ Security scenarios (assignee cannot update/delete tasks)

### Manual Testing with curl

See [API Usage Examples](#-api-usage-examples) section above for curl examples.

### Testing with Swagger UI

1. Open http://localhost:8000/api/docs/
2. Click "Authorize" button
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Click "Authorize" and "Close"
5. Now you can test all endpoints interactively

**Getting a token for Swagger:**
```bash
# Get token via curl
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Copy the "access" token and use in Swagger UI
```

## 📊 Database Schema

### Task Model

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | Integer | Primary key | Auto-increment |
| title | CharField(255) | Task title | Required |
| description | TextField | Detailed description | Optional |
| status | CharField(20) | Task status | Choices: new/in_progress/review/done |
| creator | ForeignKey(User) | Task creator | Required, related_name='created_tasks' |
| assignee | ForeignKey(User) | Assigned user | Optional, related_name='assigned_tasks' |
| deadline | DateTimeField | Task deadline | Required |
| created_at | DateTimeField | Creation timestamp | Auto-generated |
| updated_at | DateTimeField | Last update timestamp | Auto-updated |

**Indexes:**
- `(assignee, status)` - For filtering assigned tasks by status
- `(creator)` - For filtering created tasks
- `(deadline)` - For deadline-based queries and ordering

### Comment Model

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | Integer | Primary key | Auto-increment |
| task | ForeignKey(Task) | Related task | Required, related_name='comments' |
| author | ForeignKey(User) | Comment author | Required, related_name='comments' |
| text | TextField | Comment text | Required |
| created_at | DateTimeField | Creation timestamp | Auto-generated |
| updated_at | DateTimeField | Last update timestamp | Auto-updated |

**Indexes:**
- `(task)` - For fetching all comments for a task
- `(author)` - For fetching all comments by an author

## 🐳 Docker Configuration

### Services

#### web (Django Application)
- **Image**: Built from Dockerfile (Python 3.12-slim)
- **Port**: 8000 (mapped to host)
- **Volumes**: Current directory mounted to `/app` for live code editing
- **Command**: `python manage.py runserver 0.0.0.0:8000`
- **Dependencies**: PostgreSQL database

#### db (PostgreSQL 18)
- **Image**: postgres:18-alpine
- **Port**: 5432 (mapped to host)
- **Volume**: `postgres_data` for data persistence
- **Environment**: Configured via .env file

### Environment Variables

All environment variables are stored in `.env` file (not committed to git).

**Required variables:**

```env
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database configuration (DB_* variables are mapped to POSTGRES_* in docker-compose.yml)
DB_NAME=task_management
DB_USER=taskuser
DB_PASSWORD=taskpass123
DB_HOST=db
DB_PORT=5432
```

**Important Notes:**
- Only `DB_*` variables are needed in `.env`
- Docker Compose maps `DB_*` to `POSTGRES_*` for the database container
- No duplicate variables needed
- `SECRET_KEY` should be changed in production
- `DEBUG` should be `False` in production

### Docker Commands

```bash
# Build containers
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f web
docker compose logs -f db

# Stop services
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers + volumes (WARNING: deletes database!)
docker compose down -v

# Execute commands in web container
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell

# Access PostgreSQL CLI
docker compose exec db psql -U taskuser -d task_management
```

## 📝 Development

### Project Structure

```
task-management-api/
├── config/                      # Django project configuration
│   ├── __init__.py
│   ├── settings.py             # Main settings (Database, DRF, SPECTACULAR)
│   ├── urls.py                 # URL routing with API versioning
│   ├── wsgi.py
│   └── asgi.py
├── tasks/                       # Main application
│   ├── migrations/             # Database migrations
│   │   └── ...
│   ├── management/             # Custom management commands
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── create_test_data.py  # Command to create test data
│   ├── __init__.py
│   ├── models.py               # Task and Comment models with indexes
│   ├── serializers.py          # DRF serializers with validation
│   ├── views.py                # ViewSets with action-based security
│   ├── filters.py              # django-filter configuration
│   ├── urls.py                 # App-level URL routing
│   ├── tests.py                # 20+ comprehensive unit tests
│   ├── admin.py                # Django admin with inline comments
│   └── apps.py
├── docker-compose.yml          # Docker services configuration
├── Dockerfile                  # Django container definition
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
├── .env.example                # Example environment variables
├── .env                        # Actual environment variables (not in git)
├── .gitignore
└── README.md                   # This file
```

### Management Commands

#### create_test_data

Creates test users, tasks, and comments for development and testing.

```bash
docker compose exec web python manage.py create_test_data
```

**What it creates:**
- 3 users: admin (superuser), user1, user2
- 3 tasks with different statuses (NEW, IN_PROGRESS, REVIEW)
- 4 comments on tasks

**Features:**
- Idempotent: Uses `get_or_create()` to avoid duplicates
- Can be run multiple times safely
- Always updates user passwords
- Displays clear output with credentials

### Making Changes

#### Create New App

```bash
docker compose exec web python manage.py startapp myapp
```

#### Database Migrations

```bash
# Create migrations after model changes
docker compose exec web python manage.py makemigrations

# Apply migrations
docker compose exec web python manage.py migrate

# View migration SQL
docker compose exec web python manage.py sqlmigrate tasks 0001
```

#### Create Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

#### Django Shell

```bash
docker compose exec web python manage.py shell
```

### Code Style & Best Practices

This project follows:
- **PEP 8** style guide for Python code
- **Django** best practices and conventions
- **DRF** conventions for API development

**Key architectural decisions:**

1. **Security via get_queryset()**: All permission logic in ViewSet queryset filtering
2. **API Versioning**: /api/v1/ prefix for future compatibility
3. **N+1 Prevention**: Using select_related(), prefetch_related(), annotate()
4. **Validation in Serializers**: Business logic validation at serializer level (not model)
5. **Single .env file**: All environment variables in one place, mapped in docker-compose.yml

### Performance Optimization

#### N+1 Query Prevention

**In ViewSets:**
```python
def get_queryset(self):
    return Task.objects \
        .select_related('creator', 'assignee') \     # Avoid N+1 for ForeignKeys
        .prefetch_related('comments') \               # Avoid N+1 for reverse relations
        .annotate(comments_count=Count('comments'))   # Aggregate in DB, not Python
```

**In Admin:**
```python
def get_queryset(self, request):
    return super().get_queryset(request) \
        .select_related('creator', 'assignee') \
        .prefetch_related('comments')
```

#### Database Indexes

Models include strategic indexes on frequently queried fields:
- `(assignee, status)` - For user's task list filtered by status
- `(creator)` - For tasks created by user
- `(deadline)` - For deadline-based filtering and ordering

## 🔧 Troubleshooting

### Container keeps restarting

**Problem**: Web container restarts continuously with "can't open file '/app/manage.py'"

**Solution**: This happens when Django project doesn't exist yet. On first setup:
1. Temporarily change docker-compose.yml command to `sleep infinity`
2. Start containers: `docker compose up -d`
3. Create Django project: `docker compose exec web django-admin startproject config .`
4. Restore command to `python manage.py runserver 0.0.0.0:8000`
5. Restart: `docker compose restart web`

### Database connection errors

**Problem**: "could not connect to server" or "connection refused"

**Solutions**:
- Ensure database container is running: `docker compose ps`
- Check database logs: `docker compose logs db`
- Verify .env variables match docker-compose.yml
- Wait a few seconds for PostgreSQL to initialize on first run

### Port already in use

**Problem**: "bind: address already in use"

**Solutions**:
- Check what's using port 8000: `lsof -i :8000`
- Stop the conflicting service or change port in docker-compose.yml
- For database (port 5432), do the same

### Tests failing after changes

**Problem**: Tests fail after modifying models or serializers

**Solutions**:
- Ensure migrations are created: `docker compose exec web python manage.py makemigrations`
- Apply migrations: `docker compose exec web python manage.py migrate`
- Check if test URLs include /v1/ prefix
- Verify test user authentication with `self.client.force_authenticate(user=...)`

## 📄 API Response Format

### Successful Response

```json
{
  "id": 1,
  "title": "Implement new feature",
  "description": "Add user profile functionality",
  "status": "in_progress",
  "creator": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  },
  "assignee": {
    "id": 2,
    "username": "user1",
    "email": "user1@example.com"
  },
  "deadline": "2025-12-31T23:59:59Z",
  "comments_count": 3,
  "created_at": "2025-11-12T10:30:00Z",
  "updated_at": "2025-11-12T15:45:00Z"
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Нельзя перейти из статуса 'Новая' сразу в 'Выполнено'"
}
```

### Validation Error Response

```json
{
  "deadline": [
    "Срок выполнения не может быть в прошлом"
  ]
}
```

## 🚀 Production Deployment Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` in .env to a secure random value
- [ ] Set `DEBUG=False` in .env
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Use strong database password
- [ ] Configure HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure CORS if needed
- [ ] Use gunicorn instead of runserver
- [ ] Set up static file serving (collectstatic + nginx)
- [ ] Configure database backups
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Use environment-specific .env files

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Alvsok**
- GitHub: [@Alvsok](https://github.com/Alvsok)

## 🙏 Acknowledgments

- Django REST Framework documentation
- Django documentation
- PostgreSQL documentation
- drf-spectacular for excellent OpenAPI 3.0 support

---

**Project Version**: 1.0.0
**Last Updated**: 2025-11-12
