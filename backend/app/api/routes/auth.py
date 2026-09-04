from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession
from app.core.security import create_access_token
from app.schemas.auth import AuthenticatedUser, LoginRequest, RegistrationRequest, TokenResponse
from app.services.auth_service import authenticate_user, get_user_by_email, register_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(registration: RegistrationRequest, db: DbSession) -> TokenResponse:
    if get_user_by_email(db, registration.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    try:
        user = register_user(db, registration)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from None

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        user=AuthenticatedUser.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: DbSession) -> TokenResponse:
    user = authenticate_user(db, credentials.email, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        user=AuthenticatedUser.model_validate(user),
    )


@router.get("/me", response_model=AuthenticatedUser)
def read_current_user(current_user: CurrentUser) -> AuthenticatedUser:
    return AuthenticatedUser.model_validate(current_user)
