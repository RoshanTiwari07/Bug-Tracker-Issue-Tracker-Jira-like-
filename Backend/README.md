# FastAPI Template

A clean, minimal, and reusable FastAPI project template with best practices.

## Features

✨ **Clean Architecture** - Separation of concerns with proper folder structure  
🔐 **Authentication** - JWT-based auth with password hashing  
🗃️ **Database** - SQLAlchemy ORM with PostgreSQL  
📝 **API Documentation** - Auto-generated with Swagger/OpenAPI  
🧪 **Testing** - Pytest setup with sample tests  
⚙️ **Configuration** - Environment-based settings with pydantic  

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app instance
│   ├── core/                # App configuration & security
│   ├── db/                  # Database layer
│   ├── models/              # ORM models
│   ├── schemas/             # Pydantic schemas
│   ├── api/v1/              # API endpoints
│   ├── services/            # Business logic
│   ├── dependencies/        # Reusable dependencies
│   ├── utils/               # Helper functions
│   └── tests/               # Test files
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

Copy `.env` file and update with your settings:
- Update `DATABASE_URL` with your PostgreSQL connection
- Change `SECRET_KEY` to a secure random string

### 3. Run the Application

**Development mode with auto-reload:**
```bash
fastapi dev app/main.py
```

**Or using uvicorn directly:**
```bash
uvicorn app.main:app --reload
```

**Or using the main.py script:**
```bash
python -m app.main
```

### 4. Access the API

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Available Endpoints

### Public
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/v1/users/` - Create user
- `POST /api/v1/auth/login` - Login

### Protected (requires authentication)
- `GET /api/v1/users/me` - Get current user
- `POST /api/v1/items/` - Create item
- `GET /api/v1/items/` - List items
- `GET /api/v1/items/{id}` - Get item

## Testing

```bash
pytest app/tests/
```

## Database Migrations

Initialize Alembic:
```bash
alembic init app/db/migrations
```

Create migration:
```bash
alembic revision --autogenerate -m "Initial migration"
```

Apply migration:
```bash
alembic upgrade head
```

## Development

1. Create a new feature branch
2. Make your changes
3. Write tests
4. Run tests to ensure everything works
5. Commit and push

## License

MIT License - Feel free to use this template for your projects!

## Customization Tips

This is a minimal template. You can extend it with:
- Background tasks (Celery, ARQ)
- Caching (Redis)
- File uploads
- Email notifications
- Rate limiting
- Additional middleware
- Docker containerization

---

**Happy coding! 🚀**
