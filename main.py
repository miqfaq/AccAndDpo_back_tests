from fastapi import FastAPI, HTTPException, Response, Depends
from Logic.Authorisation.login import UserLoginSchema, auth_token, cookie, security, is_verified
from Logic.Authorisation.registration import UserRegisterSchema, hash_password, register_user
from DB.common import insert_user_reg_data, get_user_reg_login


app = FastAPI()

@app.post('/login')
def login(creds: UserLoginSchema, response: Response):
    print(is_verified(login=creds.username, password=creds.password))
    if is_verified(login=creds.username, password=creds.password):
        token = auth_token
        response.set_cookie(cookie, token)
        return {
            'access_token:': token
        }
    raise HTTPException(status_code= 401, detail="Incorrect login or password")

@app.post('/register', status_code=201)
def register(creds: UserRegisterSchema):
    if register_user(creds.login, creds.password):
        pass
    else:
        raise HTTPException(status_code=409, detail="Conflict")
    

@app.get('/protected', dependencies=[Depends(security.access_token_required)])
def protected():
    return {
        "data":"sec"
    }

