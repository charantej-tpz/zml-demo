# Project Guide

Comprehensive guide for setting up and developing the ZML API.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Multi-Environment Configuration](#multi-environment-configuration)
- [Firestore Setup](#firestore-setup)
- [Running the Application](#running-the-application)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Deployment](#deployment)

---

## Environment Setup

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Runtime |
| pip | Latest | Package manager |
| Docker | 20.10+ | Containerization (optional) |
| gcloud CLI | Latest | GCP interactions (for production) |

### Initial Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies (optional)
pip install -r requirements-dev.txt
```

---

## Multi-Environment Configuration

The application supports multiple environments through `.env` files.

### Environment Files

| File | Purpose |
|------|---------|
| `.env` | Base configuration (always loaded) |
| `.env.development` | Development overrides |
| `.env.staging` | Staging overrides |
| `.env.production` | Production overrides |

### Setup for Each Environment

#### Development

```bash
# Copy example and configure for development
cp .env.example .env.development

# Edit .env.development
ENVIRONMENT=development
DEBUG=true
USE_FIRESTORE_EMULATOR=true
FIRESTORE_EMULATOR_HOST=localhost:8080
LOG_LEVEL=DEBUG
LOG_JSON_FORMAT=false
```

#### Staging

```bash
# Create staging configuration
cp .env.example .env.staging

# Edit .env.staging
ENVIRONMENT=staging
DEBUG=false
SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/staging-credentials.json
REALTIME_DATABASE_URL=https://your-staging-project.firebaseio.com
USE_FIRESTORE_EMULATOR=false
LOG_LEVEL=INFO
LOG_JSON_FORMAT=true
CORS_ORIGINS=https://staging.yourdomain.com
```

#### Production

```bash
# Create production configuration
cp .env.example .env.production

# Edit .env.production
ENVIRONMENT=production
DEBUG=false
SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/prod-credentials.json
REALTIME_DATABASE_URL=https://your-production-project.firebaseio.com
USE_FIRESTORE_EMULATOR=false
LOG_LEVEL=WARNING
LOG_JSON_FORMAT=true
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### Switching Environments

```bash
# Method 1: Set ENVIRONMENT variable
export ENVIRONMENT=staging
uvicorn app.main:app

# Method 2: Use specific .env file
cp .env.staging .env
uvicorn app.main:app
```

---

## Firestore Setup

### Option 1: Local Emulator (Development)

```bash
# Install Firebase CLI (if not installed)
npm install -g firebase-tools

# Start Firestore emulator
firebase emulators:start --only firestore

# Or use Docker Compose
docker-compose up firestore-emulator
```

Configure `.env`:
```bash
USE_FIRESTORE_EMULATOR=true
FIRESTORE_EMULATOR_HOST=localhost:8080
```

### Option 2: GCP Firestore (Staging/Production)

1. **Create a GCP Project** with Firestore enabled

2. **Create Service Account:**
   ```bash
   gcloud iam service-accounts create zml-api-sa \
     --display-name="ZML API Service Account"

   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:zml-api-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/datastore.user"

   gcloud iam service-accounts keys create credentials.json \
     --iam-account=zml-api-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

3. **Configure `.env`:**
   ```bash
   SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/credentials.json
   REALTIME_DATABASE_URL=https://your-project-id.firebaseio.com
   USE_FIRESTORE_EMULATOR=false
   ```

---

## Running the Application

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Using Docker

```bash
# Build image
docker build -t zml-api .

# Run container
docker run -p 8080:8080 --env-file .env zml-api
```

### Using Docker Compose (Recommended for Development)

```bash
# Start all services (API + Firestore emulator)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

---

## Development Workflow

### Architecture Overview

The application follows SOLID principles with a layered architecture:

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────────┐     ┌───────────────┐
│  Endpoint   │ --> │    Service      │ --> │    Repository       │ --> │   Database    │
│  (API)      │     │  (Logic)        │     │  (Data Access)      │     │  (Firebase)   │
└─────────────┘     └─────────────────┘     └─────────────────────┘     └───────────────┘
       │                    │                        │
   Depends on:          Depends on:              Uses:
   IService            IRepository           RealtimeDBOperations
```

| Layer | Responsibility | Location |
|-------|----------------|----------|
| Endpoint | HTTP handling, validation | `app/api/v1/endpoints/` |
| Service | Business logic | `app/services/` |
| Repository | Data access | `app/repositories/` |
| Database | Low-level Firebase ops | `app/db/` |

### Adding a New Feature (SOLID Pattern)

#### 1. Create Repository Interface

```python
# app/interfaces/repositories/users.py
from abc import abstractmethod
from app.interfaces.repositories.base import IRepository

class IUserRepository(IRepository[UserData]):
    """Domain-specific interface for user operations."""

    @abstractmethod
    async def get_by_email(self, email: str) -> UserData:
        pass
```

#### 2. Create Repository Implementation

```python
# app/repositories/user_repository.py
from app.interfaces.repositories.users import IUserRepository
from app.db.realtime_db import RealtimeDBOperations

class UserRepository(IUserRepository):
    def __init__(self, rdb: RealtimeDBOperations):
        self.rdb = rdb  # Low-level DB operations

    async def get_by_email(self, email: str) -> UserData:
        # Implement data access...
        pass
```

#### 3. Create Service Interface

```python
# app/interfaces/users.py
from abc import ABC, abstractmethod

class IUserService(ABC):
    @abstractmethod
    async def create_user(self, data: dict) -> str:
        pass
```

#### 4. Create Service Implementation

```python
# app/services/users.py
from app.interfaces.repositories.users import IUserRepository
from app.interfaces.users import IUserService

class UserService(IUserService):
    def __init__(self, repo: IUserRepository):
        self.repo = repo  # Depends on abstraction!

    async def create_user(self, data: dict) -> str:
        # Business logic here
        return await self.repo.create(data)
```

#### 5. Create Schema

```python
# app/schemas/user.py
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
```

#### 6. Create Endpoint with Dependency Injection

```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
from app.db.realtime_db import RealtimeDBOperations
from app.interfaces.users import IUserService
from app.repositories.user_repository import UserRepository
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service() -> IUserService:
    """Wire up the dependency chain."""
    rdb = RealtimeDBOperations(base_path="users")
    repo = UserRepository(rdb)
    return UserService(repo)

@router.post("/")
async def create_user(
    data: UserCreate,
    service: IUserService = Depends(get_user_service)
):
    return await service.create_user(data.model_dump())
```

#### 7. Register Router

```python
# app/api/v1/router.py
from app.api.v1.endpoints import users
router.include_router(users.router)
```

### SOLID Compliance

| Principle | Implementation |
|-----------|---------------|
| **S**ingle Responsibility | Service = logic, Repository = data access |
| **O**pen/Closed | Add new features without modifying existing code |
| **L**iskov Substitution | Swap Firebase for PostgreSQL via interface |
| **I**nterface Segregation | Each domain has focused interface |
| **D**ependency Inversion | Service → IRepository (abstraction) |

### Project Structure

```
app/
├── interfaces/
│   ├── repositories/       # Repository abstractions
│   │   ├── base.py         # IRepository[T]
│   │   └── vitals.py       # IVitalsRepository
│   ├── vitals.py           # IVitalsService
│   └── authentication.py   # IAuthenticationService
├── repositories/
│   ├── base.py             # BaseRepository (Firestore)
│   ├── realtime_base.py    # RealtimeBaseRepository
│   └── vitals_repository.py
├── services/
│   ├── vitals.py
│   └── authentication.py
├── db/
│   ├── firestore.py        # Firestore operations
│   └── realtime_db.py      # Realtime DB operations
└── api/v1/endpoints/
    ├── vitals.py
    └── authentication.py
```

### Example: Adding "Medications" Feature

#### Files to Create

```
app/
├── interfaces/
│   ├── repositories/
│   │   └── medications.py         ← 1. IRepository interface
│   └── medications.py             ← 2. IService interface
├── schemas/
│   └── medications.py             ← 3. Pydantic models
├── repositories/
│   └── medications_repository.py  ← 4. Data access
├── services/
│   └── medications.py             ← 5. Business logic
└── api/v1/endpoints/
    └── medications.py             ← 6. HTTP endpoint
```

#### What Each File Does

| # | File | Purpose | Contains |
|---|------|---------|----------|
| 1 | `interfaces/repositories/medications.py` | Contract for data ops | `IMedicationsRepository` |
| 2 | `interfaces/medications.py` | Contract for business logic | `IMedicationsService` |
| 3 | `schemas/medications.py` | Request/response validation | `MedicationCreate`, `MedicationResponse` |
| 4 | `repositories/medications_repository.py` | Firebase CRUD | Uses `RealtimeDBOperations` |
| 5 | `services/medications.py` | Logic (dosage calc, validation) | Depends on `IMedicationsRepository` |
| 6 | `api/v1/endpoints/medications.py` | HTTP routes | `POST /medications`, wires dependencies |

#### Dependency Flow

```
POST /api/v1/medications
           ↓
   ┌───────────────────┐
   │  Endpoint (HTTP)  │  ← Handles request, injects service
   └─────────┬─────────┘
             ↓
   ┌───────────────────┐
   │  Service (Logic)  │  ← Business rules, validation
   └─────────┬─────────┘
             ↓
   ┌───────────────────┐
   │ Repository (Data) │  ← CRUD operations
   └─────────┬─────────┘
             ↓
   ┌───────────────────┐
   │ RealtimeDB (Firebase) │  ← Low-level SDK
   └───────────────────┘
```

#### Final Step: Register Router

```python
# app/api/v1/router.py
from app.api.v1.endpoints import medications
router.include_router(medications.router)
```

---

## Testing

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures (client, mocks)
├── test_api.py          # Root endpoint & routing tests
├── test_health.py       # Health check endpoint tests
└── test_settings.py     # Configuration tests
```

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Run with HTML coverage report
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Run specific test file
pytest tests/test_health.py -v

# Run specific test class
pytest tests/test_settings.py::TestSettings -v

# Run single test
pytest tests/test_health.py::TestHealthEndpoints::test_health_check -v
```

### Quick Test Commands

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest -x` | Stop on first failure |
| `pytest --tb=short` | Shorter tracebacks |
| `pytest --lf` | Run only last failed tests |
| `pytest -k "health"` | Run tests matching "health" |

### Test Fixtures (conftest.py)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `client` | session | TestClient for HTTP requests |
| `mock_firestore_client` | session | Mocked Firestore client |
| `mock_firebase_app` | session | Mocked Firebase Admin app |
| `mock_settings` | function | Test settings instance |
| `mock_realtime_db` | function | Mocked Realtime DB operations |

### Writing Tests

```python
# tests/test_users.py
class TestUserEndpoints:
    """Test suite for user endpoints."""

    def test_create_user(self, client):
        """Test user creation."""
        response = client.post("/api/v1/users", json={
            "name": "John Doe",
            "email": "john@example.com"
        })
        assert response.status_code == 201
        assert response.json()["name"] == "John Doe"

    def test_get_user_not_found(self, client):
        """Test 404 for missing user."""
        response = client.get("/api/v1/users/nonexistent")
        assert response.status_code == 404
```

### Watch Mode (Auto-rerun on Changes)

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw tests/
```

---

## Deployment

### Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/zml-api

# Deploy to Cloud Run
gcloud run deploy zml-api \
  --image gcr.io/YOUR_PROJECT_ID/zml-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars "ENVIRONMENT=production,GCP_PROJECT_ID=YOUR_PROJECT_ID"
```

### Kubernetes

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zml-api
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: zml-api
          image: gcr.io/YOUR_PROJECT_ID/zml-api:latest
          ports:
            - containerPort: 8080
          envFrom:
            - secretRef:
                name: zml-api-secrets
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: 8080
          readinessProbe:
            httpGet:
              path: /api/v1/health/ready
              port: 8080
```

---

## Common Issues

### Firestore Connection Errors

- **Emulator not running**: Start with `firebase emulators:start --only firestore`
- **Wrong credentials**: Verify `GOOGLE_APPLICATION_CREDENTIALS` path
- **Permission denied**: Check service account IAM roles

### Import Errors

- **Module not found**: Ensure virtual environment is activated
- **Circular imports**: Check import order in `__init__.py` files
