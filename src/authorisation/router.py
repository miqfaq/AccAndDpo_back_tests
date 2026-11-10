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
async def login(creds: UserLoginSchema, response: Response):
    if not await is_verified(login=creds.login, password=creds.password):
        raise HTTPException(status_code=401, detail="Incorrect login or password")

    token = await get_token(creds.login)
    security.set_access_cookies(token, response, max_age=99999)
    return {"access_token": token}

@router.post('/register', status_code=201)
async def register(creds: UserRegisterSchema):
    if await register_user(creds.login, creds.password):
        return "Sucess!"
    else:
        raise HTTPException(status_code=409, detail="Conflict")


@router.post('/addRole')
async def add_role (uid, role, payload: TokenPayload = Depends(require_role('admin'))):
    await add_userRole(uid, role)
