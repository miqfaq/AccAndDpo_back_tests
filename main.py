from fastapi import FastAPI
from src.authorisation.router import router as auth_router
from src.profile.router import router as userpage_routrer
from src.testEngine.router import router as testengine_router
from src.security.security import security, JWTDecodeError, Request, JSONResponse




app = FastAPI()

app.include_router(auth_router)
app.include_router(userpage_routrer)
app.include_router(testengine_router)
security.handle_errors(app)

@app.exception_handler(JWTDecodeError)
async def jwt_decode_error_handler(request: Request, exc: JWTDecodeError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Токен недействителен или истёк"},
        headers={"WWW-Authenticate": "Bearer"},
    )