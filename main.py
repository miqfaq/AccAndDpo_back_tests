from fastapi import FastAPI
from src.authorisation.router import router as auth_router
from src.profile.router import router as userpage_routrer
from src.testEngine.router import router as testengine_router




app = FastAPI()

app.include_router(auth_router)
app.include_router(userpage_routrer)
app.include_router(testengine_router)
