from fastapi import APIRouter
from fastapi import Depends
from .major import router as major_router
from server.auth.login import manager as login_manager

router = APIRouter()
router.include_router(major_router, prefix="/major", tags=["major"])


@router.get('/protected')
def protected_route(user=Depends(login_manager)):
    print(user)
    return user.password
