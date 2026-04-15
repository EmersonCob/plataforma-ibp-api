from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_manager
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserListResponse, UserRead, UserStatusUpdate, UserUpdate
from app.services.users import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
def list_users(
    search: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
) -> UserListResponse:
    items, total = user_service.list(db, search=search, page=page, size=size)
    return UserListResponse(items=items, total=total, page=page, size=size)


@router.post("", response_model=UserRead, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db), actor: User = Depends(require_manager)) -> UserRead:
    return user_service.create(db, payload, actor)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, db: Session = Depends(get_db), _: User = Depends(require_manager)) -> UserRead:
    return user_service.get(db, user_id)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_manager),
) -> UserRead:
    return user_service.update(db, user_id, payload, actor)


@router.patch("/{user_id}/status", response_model=UserRead)
def update_user_status(
    user_id: str,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_manager),
) -> UserRead:
    return user_service.update_status(db, user_id, payload.is_active, actor)
