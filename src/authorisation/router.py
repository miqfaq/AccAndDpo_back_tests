from fastapi import HTTPException, Response, APIRouter, Depends
from src.security.security import security
from src.authorisation.login import UserLoginSchema, cookie, is_verified, get_token, require_role, add_userRole
from src.authorisation.registration import UserRegisterSchema, register_user
from authx import TokenPayload



router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post('/login')
def login(creds: UserLoginSchema, response: Response):
    if not is_verified(login=creds.username, password=creds.password):
        raise HTTPException(status_code=401, detail="Incorrect login or password")

    token = get_token(creds.username)
    security.set_access_cookies(token, response)
    return {"access_token": token}

@router.post('/register', status_code=201)
def register(creds: UserRegisterSchema):
    if register_user(creds.login, creds.password):
        pass
    else:
        raise HTTPException(status_code=409, detail="Conflict")


@router.post('/addRole')
def add_role (uid, role, payload: TokenPayload = Depends(require_role('admin'))):
    add_userRole(uid, role)
