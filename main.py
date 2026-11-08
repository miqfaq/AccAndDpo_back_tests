from fastapi import FastAPI
from src.authorisation.router import router as auth_router
from src.profile.router import router as userpage_routrer
from src.testEngine.router import router as testengine_router
from src.admin.router import router as admin_router
from src.dpo.router import router as dpo_router
from src.security.security import security, JWTDecodeError, Request, JSONResponse
from src.GigaChatIntegration.router import router as gigachat_router




app = FastAPI()

app.include_router(auth_router)
app.include_router(userpage_routrer)
app.include_router(testengine_router)
app.include_router(admin_router)
app.include_router(dpo_router)
app.include_router(gigachat_router)
security.handle_errors(app)

@app.exception_handler(JWTDecodeError)
async def jwt_decode_error_handler(request: Request, exc: JWTDecodeError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Токен недействителен или истёк"},
        headers={"WWW-Authenticate": "Bearer"},
    )