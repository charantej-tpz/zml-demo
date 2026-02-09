# Feature Development Guide

Step-by-step guide to add a new feature following SOLID principles.

---

## Quick Reference

| Database | Variable Name | Import |
|----------|--------------|--------|
| Firestore | `db` | `from app.db.firestore import get_firestore_client` |
| Realtime DB | `rdb` | `from app.db.realtime_db import get_realtime_client` |

---

## Step 1: Create Repository Interface

**File:** `app/interfaces/repositories/{feature_name}.py`

```python
from abc import abstractmethod
from typing import Any, Dict, Optional
from app.interfaces.repositories.base import IRepository


class I{Feature}Repository(IRepository[Dict[str, Any]]):
    """Interface for {feature} repository operations."""

    @abstractmethod
    async def get_{feature}(self, user_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def set_{feature}(self, user_id: str, data: Dict[str, Any]) -> None:
        pass
```

---

## Step 2: Create Service Interface

**File:** `app/interfaces/{feature_name}.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class I{Feature}Service(ABC):
    """Interface for {feature} service operations."""

    @abstractmethod
    async def get_{feature}(self, user_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def create_{feature}(self, user_id: str, **kwargs) -> Dict[str, Any]:
        pass
```

---

## Step 3: Create Schema

**File:** `app/schemas/{feature_name}.py`

```python
from pydantic import BaseModel, Field


class {Feature}Request(BaseModel):
    """Request schema."""
    field1: str = Field(..., description="Description")
    field2: float = Field(..., gt=0, description="Description")


class {Feature}Response(BaseModel):
    """Response schema."""
    user_id: str
    field1: str
    field2: float
```

---

## Step 4: Create Repository

**File:** `app/repositories/{feature_name}_repository.py`

### Option A: Firestore (db)

```python
import logging
from typing import Any, Dict, List, Optional
from google.cloud.firestore_v1 import Client
from app.core.exceptions import DatabaseError
from app.db.firestore import get_firestore_client
from app.interfaces.repositories.{feature_name} import I{Feature}Repository

logger = logging.getLogger(__name__)
COLLECTION_NAME = "{feature_name}"


class {Feature}Repository(I{Feature}Repository):

    def __init__(self, db: Optional[Client] = None) -> None:
        self._db = db

    @property
    def db(self) -> Client:
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = self.db.collection(COLLECTION_NAME).document(id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Error: {e}")
            raise DatabaseError(detail=str(e)) from e

    async def create(self, data: Dict[str, Any], id: Optional[str] = None) -> str:
        try:
            self.db.collection(COLLECTION_NAME).document(id).set(data, merge=True)
            return id
        except Exception as e:
            raise DatabaseError(detail=str(e)) from e

    # Implement other IRepository methods...

    async def get_{feature}(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.get_by_id(user_id)

    async def set_{feature}(self, user_id: str, data: Dict[str, Any]) -> None:
        await self.create(data, user_id)
```

### Option B: Realtime Database (rdb)

```python
import logging
from typing import Any, Dict, Optional
from app.core.exceptions import DatabaseError
from app.db.realtime_db import RealtimeDBOperations
from app.interfaces.repositories.{feature_name} import I{Feature}Repository

logger = logging.getLogger(__name__)


class {Feature}Repository(I{Feature}Repository):

    def __init__(self, rdb: RealtimeDBOperations) -> None:
        self.rdb = rdb

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.rdb.get(f"users/{id}/{feature_name}")
        except Exception as e:
            raise DatabaseError(detail=str(e)) from e

    async def create(self, data: Dict[str, Any], id: Optional[str] = None) -> str:
        try:
            self.rdb.set(f"users/{id}/{feature_name}", data)
            return id
        except Exception as e:
            raise DatabaseError(detail=str(e)) from e

    # Implement other methods...
```

---

## Step 5: Create Service

**File:** `app/services/{feature_name}.py`

```python
import logging
from typing import Any, Dict, Optional
from app.core.exceptions import DatabaseError
from app.interfaces.{feature_name} import I{Feature}Service
from app.interfaces.repositories.{feature_name} import I{Feature}Repository

logger = logging.getLogger(__name__)


class {Feature}Service(I{Feature}Service):

    def __init__(self, repo: I{Feature}Repository) -> None:
        self.repo = repo

    async def get_{feature}(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            logger.info(f"Getting {feature} for user: {user_id}")
            data = await self.repo.get_{feature}(user_id)
            if data:
                data["user_id"] = user_id
            return data
        except DatabaseError:
            raise
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise DatabaseError(detail=str(e)) from e

    async def create_{feature}(self, user_id: str, **kwargs) -> Dict[str, Any]:
        try:
            logger.info(f"Creating {feature} for user: {user_id}")
            data = {**kwargs}
            await self.repo.set_{feature}(user_id, data)
            return {"user_id": user_id, **data}
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(detail=str(e)) from e
```

---

## Step 6: Create Endpoint

**File:** `app/api/v1/endpoints/{feature_name}.py`

### Firestore Version

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.interfaces.{feature_name} import I{Feature}Service
from app.repositories.{feature_name}_repository import {Feature}Repository
from app.schemas.{feature_name} import {Feature}Request, {Feature}Response
from app.services.{feature_name} import {Feature}Service

router = APIRouter(prefix="/{feature-name}", tags=["{Feature}"])


def get_{feature}_service() -> I{Feature}Service:
    """Dependency: Firestore -> Repository -> Service"""
    repo = {Feature}Repository()  # Uses Firestore (db)
    return {Feature}Service(repo)


@router.get("/{user_id}", response_model={Feature}Response)
async def get_{feature}(
    user_id: str,
    service: I{Feature}Service = Depends(get_{feature}_service),
):
    result = await service.get_{feature}(user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return result


@router.post("/{user_id}", response_model={Feature}Response)
async def create_{feature}(
    user_id: str,
    request: {Feature}Request,
    service: I{Feature}Service = Depends(get_{feature}_service),
):
    return await service.create_{feature}(user_id=user_id, **request.model_dump())
```

### Realtime DB Version

```python
from app.db.realtime_db import get_realtime_client

def get_{feature}_service() -> I{Feature}Service:
    """Dependency: RDB -> Repository -> Service"""
    rdb = get_realtime_client(base_path="your_base_path")
    repo = {Feature}Repository(rdb)
    return {Feature}Service(repo)
```

---

## Step 7: Register Router

**File:** `app/api/v1/router.py`

```python
from app.api.v1.endpoints import {feature_name}

router.include_router({feature_name}.router)
```

---

## Step 8: Run Tests

```bash
./venv/bin/pytest tests/ -v
```

---

## File Checklist

| # | File | Location |
|---|------|----------|
| 1 | Repository Interface | `app/interfaces/repositories/{feature}.py` |
| 2 | Service Interface | `app/interfaces/{feature}.py` |
| 3 | Schema | `app/schemas/{feature}.py` |
| 4 | Repository | `app/repositories/{feature}_repository.py` |
| 5 | Service | `app/services/{feature}.py` |
| 6 | Endpoint | `app/api/v1/endpoints/{feature}.py` |
| 7 | Register | `app/api/v1/router.py` |

---

## Dependency Flow

```
Endpoint → Service → Repository → Database
   ↓          ↓           ↓
IService  IRepository   db/rdb
```
