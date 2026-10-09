from fastapi import FastAPI
from src.authorisation.router import router as auth_router
from src.userPage.router import router as userpage_routrer
from src.tests.router import router as testpage_router



app = FastAPI()

app.include_router(auth_router)
app.include_router(userpage_routrer)
app.include_router(testpage_router)
