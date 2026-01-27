# Bug Tracker Backend API

A production-ready bug tracking system built with FastAPI, PostgreSQL, and Docker. Complete with user management, project management, ticketing system, comments, file attachments, and advanced search capabilities.

## ✨ Features

### Core Features
- 🔐 **User Authentication** - JWT-based login/register with secure password hashing
- 👥 **User Management** - CRUD operations, admin controls, user activation/deactivation
- 📋 **Projects** - Create and manage projects, control project members
- 🎫 **Tickets** - Create tickets with auto-generated keys, assign to users, track status
- 💬 **Comments** - Add nested comments to tickets, threaded discussions
- 📎 **Attachments** - Upload, download, and manage files with validation
- 🔍 **Advanced Search** - Keyword search, filtering by status/priority/type, custom sorting, pagination

### API Documentation
- 📖 Swagger UI (`/docs`)
- 📘 Scalar UI (`/scalar`)
- 📚 ReDoc (`/redoc`)

### Architecture & Quality
- ✨ **Clean Architecture** - Separation of concerns with proper folder structure
- 📝 **Auto-generated API Documentation** - Swagger/OpenAPI built-in
- 🧪 **Testing** - Pytest setup with comprehensive tests
- ⚙️ **Configuration** - Environment-based settings with Pydantic
- 🐳 **Docker Ready** - Multi-stage optimized build (489MB, 59% reduction)

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | FastAPI (Python 3.13) |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy + SQLModel |
| Authentication | JWT with python-jose |
| Password Hashing | bcrypt |
| Migrations | Alembic |
| Validation | Pydantic |
| Testing | Pytest |
| Containerization | Docker & Docker Compose |

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app instance
│   ├── api/v1/                    # All API endpoints
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── users.py              # User management
│   │   ├── projects.py           # Projects CRUD
│   │   ├── tickets.py            # Tickets + advanced search
│   │   ├── comments.py           # Comments
│   │   ├── attachments.py        # File attachments
│   │   └── router.py             # Main router
│   ├── services/                  # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── project_service.py
│   │   ├── tickets.py
│   │   ├── comment_service.py
│   │   ├── attachment_service.py
│   │   └── base.py               # Base service
│   ├── models/                    # Database ORM models
│   ├── schemas/                   # Pydantic request/response schemas
│   ├── dependencies/              # Reusable dependency injection
│   ├── core/                      # Configuration, logging, security
│   ├── db/                        # Database setup, session, migrations
│   ├── utils/                     # Helper functions
│   ├── tests/                     # Unit and integration tests
│   └── uploads/                   # File storage directory
├── Dockerfile                     # Multi-stage production build
├── .dockerignore                  # Docker ignore patterns
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
├── alembic.ini                    # Database migration config
├── main.py                        # Application entry point
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OR Python 3.13+ and PostgreSQL 16+

### Option 1: Docker (Recommended)

#### 1. Setup Environment

```bash
# Navigate to project root
cd "c:\Myprojects\Bug Tracker"

# Copy environment file
cp .env.example .env

# Edit .env with your settings
```

#### 2. Start Development Environment

```bash
# Start backend + database
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

#### 3. Access the Application

- **API Swagger UI:** http://localhost:8000/docs
- **API Scalar UI:** http://localhost:8000/scalar
- **API ReDoc:** http://localhost:8000/redoc
- **Backend Server:** http://localhost:8000
- **Database:** localhost:5432 (PostgreSQL)

### Option 2: Local Development

#### 1. Install Dependencies

```bash
cd Backend
pip install -r requirements.txt
```

#### 2. Setup Database

```bash
# Create database
psql -U postgres -c "CREATE DATABASE bug_tracker;"

# Run migrations
alembic upgrade head
```

#### 3. Setup Environment

```bash
# Copy and edit .env file
cp .env.example .env
```

#### 4. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📊 API Endpoints

### Authentication
```
POST   /api/v1/auth/register        # Register new user
POST   /api/v1/auth/login           # Login and get JWT token
POST   /api/v1/auth/refresh         # Refresh access token
```

### Users
```
POST   /api/v1/users/               # Create user (admin)
GET    /api/v1/users                # List all users (with pagination)
GET    /api/v1/users/me             # Get current user profile
GET    /api/v1/users/{id}           # Get specific user
PUT    /api/v1/users/me             # Update own profile
PATCH  /api/v1/users/{id}/activate  # Activate user (admin)
PATCH  /api/v1/users/{id}/deactivate # Deactivate user (admin)
DELETE /api/v1/users/{id}           # Delete user (admin)
```

### Projects
```
POST   /api/v1/projects/            # Create project
GET    /api/v1/projects             # List projects
GET    /api/v1/projects/{id}        # Get project details
PUT    /api/v1/projects/{id}        # Update project
DELETE /api/v1/projects/{id}        # Delete project
POST   /api/v1/projects/{id}/members # Add project member
DELETE /api/v1/projects/{id}/members/{user_id} # Remove member
```

### Tickets
```
POST   /api/v1/tickets                      # Create ticket
GET    /api/v1/tickets/{project_name}/search # Advanced search & filter
GET    /api/v1/tickets/{id}                 # Get ticket details
PATCH  /api/v1/tickets/{id}                 # Update ticket
PATCH  /api/v1/tickets/{id}/status          # Change ticket status
DELETE /api/v1/tickets/{id}                 # Delete ticket
```

**Search Parameters:**
```
keyword      # Search in title, description, ticket key
status       # Filter by status (todo, in_progress, in_review, done, cancelled)
priority     # Filter by priority (low, medium, high, critical)
issue_type   # Filter by type (bug, feature, task)
assignee_id  # Filter by assignee user ID
reporter_id  # Filter by reporter user ID
sort_by      # Sort field (created_at, updated_at, priority, status, title)
sort_order   # asc or desc
skip         # Pagination offset (default: 0)
limit        # Results per page (default: 20)
```

**Example Search:**
```
GET /api/v1/tickets/MyProject/search?keyword=bug&priority=critical&sort_by=created_at&sort_order=desc
```

### Comments
```
POST   /api/v1/tickets/{id}/comments        # Add comment to ticket
GET    /api/v1/tickets/{id}/comments        # List all comments
PATCH  /api/v1/comments/{id}                # Edit comment
DELETE /api/v1/comments/{id}                # Delete comment
POST   /api/v1/comments/{id}/reply          # Reply to comment
```

### Attachments
```
POST   /api/v1/attachments/tickets/{id}/upload           # Upload file
GET    /api/v1/attachments/tickets/{id}/attachments      # List ticket attachments
GET    /api/v1/attachments/{id}/download                 # Download file
DELETE /api/v1/attachments/{id}                          # Delete file
GET    /api/v1/attachments/users/{user_id}/attachments   # List user's files
```

---

## 💻 Commands to Run Backend

### 1️⃣ Docker Mode (Production)

```bash
# Build Docker image
docker build -t bug-tracker-backend:latest -f Backend/Dockerfile Backend

# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# View live logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### 2️⃣ Local Development (Without Docker)

```bash
# Install dependencies
cd Backend
pip install -r requirements.txt

# Apply database migrations
alembic upgrade head

# Run FastAPI with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access at http://localhost:8000/docs
```

### 3️⃣ Database Operations

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d bug_tracker

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Your description"

# Apply all pending migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# View current migration status
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history
```

### 4️⃣ Testing

```bash
# Run all tests
docker-compose exec backend pytest

# Run with verbose output
docker-compose exec backend pytest -v

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py -v

# Run with coverage report
docker-compose exec backend pytest --cov=app tests/

# Run tests matching pattern
docker-compose exec backend pytest -k "test_login" -v
```

### 5️⃣ Docker Management

```bash
# Build Docker image
docker build -t bug-tracker-backend:latest -f Backend/Dockerfile Backend

# View image size
docker images bug-tracker-backend:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# List all running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View container logs
docker logs container_name -f

# View last 100 lines of logs
docker logs container_name --tail 100

# Stop all containers
docker-compose down

# Remove unused images
docker image prune -a

# Inspect image
docker inspect bug-tracker-backend:latest

# Execute command in running container
docker-compose exec backend python -c "print('Hello')"
```

### 6️⃣ Container Shell Access

```bash
# Access backend container shell
docker-compose exec backend /bin/bash

# Access database container
docker-compose exec db psql -U postgres -d bug_tracker

# Execute Python command
docker-compose exec backend python -c "import app; print('App loaded')"

# Check Python version
docker-compose exec backend python --version

# List installed packages
docker-compose exec backend pip list

# Install additional package in running container
docker-compose exec backend pip install package_name
```

### 7️⃣ Health & Monitoring

```bash
# Check API health
curl http://localhost:8000/health

# Check container status
docker-compose ps

# View container resource usage
docker stats

# View environment variables in container
docker-compose exec backend env

# Generate new SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 8️⃣ Code Quality & Formatting

```bash
# Format code with black
docker-compose exec backend black app/

# Run linter (pylint)
docker-compose exec backend pylint app/

# Check dependencies
docker-compose exec backend pip check

# View dependency tree
docker-compose exec backend pipdeptree
```

---

## 🔧 Environment Configuration (.env)

```ini
# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
DB_HOST=db              # Use 'db' for Docker, 'localhost' for local
DB_PORT=5432
DB_NAME=bug_tracker

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Application
APP_NAME=Bug Tracker
DEBUG=False
LOG_LEVEL=INFO
```

**To generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🔐 Security Features

- ✅ JWT authentication with refresh tokens
- ✅ Password hashing with bcrypt
- ✅ CORS protection
- ✅ Pydantic input validation
- ✅ SQL injection prevention (ORM)
- ✅ Non-root user in Docker (UID 1000)
- ✅ Health checks enabled
- ✅ Capability dropping in production
- ✅ Environment-based configuration

---

## 📈 Performance Metrics

- **Docker Image Size:** 489MB (multi-stage optimized, 59% reduction from ~1.2GB)
- **Startup Time:** ~5-10 seconds
- **Database:** Async connection pooling enabled
- **API Response:** <100ms average

---

## 🐛 Troubleshooting

### Port 8000 Already in Use

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
lsof -i :8000
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check if services are running
docker-compose ps

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Reset database (WARNING: data loss)
docker-compose down -v
docker-compose up -d
```

### Build Failures

```bash
# Clean rebuild
docker-compose down -v
docker-compose up -d --build

# View build logs
docker-compose logs backend
```

### Container Not Starting

```bash
# Check logs
docker-compose logs backend

# Verify image
docker images | grep bug-tracker

# Recreate container
docker-compose down
docker-compose up -d --force-recreate
```

---

## 📚 API Documentation URLs

Once the backend is running, access:

- **Swagger UI (Interactive):** http://localhost:8000/docs
- **Scalar UI (Modern):** http://localhost:8000/scalar
- **ReDoc (Clean):** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## 📊 Project Status

✅ User Authentication & Management  
✅ Projects Management  
✅ Tickets with Auto-generated Keys  
✅ Comments with Threading  
✅ File Attachments  
✅ Advanced Search & Filtering  
✅ Docker Containerization  
✅ Database Migrations  
✅ API Documentation  
✅ Unit Tests  
✅ Security Hardening  
✅ Production Ready  

---

## 📞 Support Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation:** https://www.sqlalchemy.org/
- **Docker Documentation:** https://docs.docker.com/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **Python Alembic:** https://alembic.sqlalchemy.org/

---

**Version:** 1.0.0  
**Status:** Production Ready ✅  
**Last Updated:** January 27, 2026
