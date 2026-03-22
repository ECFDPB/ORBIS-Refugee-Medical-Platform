from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth, documents, passport, frontend
from routers import navigator

app = FastAPI(
    title="Refugee Medical Platform API",
    description="MVP backend for the refugee medical health passport system.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(frontend.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(passport.router)
app.include_router(navigator.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
