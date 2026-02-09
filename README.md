# ZML API

A production-grade FastAPI boilerplate with Firebase integration, following SOLID principles.

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 🔥 **Firebase** - Firestore + Realtime Database with emulator support
- 🏗️ **SOLID Architecture** - Repository pattern with interfaces
- 🔐 **Firebase Auth** - JWT token authentication
- ⚙️ **Multi-environment** - Development, staging, and production configs
- 📝 **Production Logging** - JSON logs with request tracing
- 🐳 **Docker** - Containerized deployment
- ✅ **Testing** - Pytest with 100% passing tests

## API Endpoints

| Method | Endpoint | Description | Database |
|--------|----------|-------------|----------|
| GET | `/api/v1/health` | Health check | - |
| POST | `/api/v1/authentication/register` | Register user | Firebase Auth |
| GET | `/api/v1/authentication/me` | Get current user | Firebase Auth |
| POST | `/api/v1/vitals/{user_id}` | Update vitals | Realtime DB |
| GET | `/api/v1/medical-info/{user_id}` | Get medical info | Firestore |
| POST | `/api/v1/medical-info/{user_id}` | Set medical info | Firestore |

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Run the server
uvicorn app.main:app --reload --port 8080
```

**Access:** http://localhost:8080/docs

## Architecture

```
Endpoint → Service → Repository → Database
   ↓          ↓           ↓
IService  IRepository   db/rdb
```

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Endpoints | `app/api/v1/endpoints/` | HTTP handling |
| Services | `app/services/` | Business logic |
| Repositories | `app/repositories/` | Data access |
| Interfaces | `app/interfaces/` | Contracts (SOLID) |
| Database | `app/db/` | Firebase connections |

## Database Access

| Database | Variable | Function |
|----------|----------|----------|
| Firestore | `db` | `get_firestore_client()` |
| Realtime DB | `rdb` | `get_realtime_client()` |

## Project Structure

```
app/
├── api/v1/endpoints/     # API routes
├── interfaces/           # Abstract interfaces (SOLID)
│   └── repositories/     # Repository interfaces
├── services/             # Business logic
├── repositories/         # Data access layer
├── schemas/              # Pydantic models
├── db/                   # Firebase clients
├── core/                 # Exceptions, logging
├── middleware/           # Request context
└── main.py               # Entry point
```

## Documentation

| Document | Purpose |
|----------|---------|
| [PROJECT_GUIDE.md](PROJECT_GUIDE.md) | Setup & development guide |
| [FEATURE.md](FEATURE.md) | Step-by-step feature development |

## License

MIT
