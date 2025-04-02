from contextlib import asynccontextmanager
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from src.authentication.router import router as router_authentication
from src.accounts.router import router as router_accounts

import uvicorn


app = FastAPI(
    title="Audio service by povepo", 
    docs_url='/ui-swagger',
)

app.include_router(router_authentication)
app.include_router(router_accounts)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

if __name__ == "__main__":
    uvicorn.run("main:app", host='localhost', port=8080, reload=True)