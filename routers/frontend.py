"""
Frontend Router — serves Jinja2 HTML pages
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["frontend"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def splash(request: Request):
    return templates.TemplateResponse("splash.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/account", response_class=HTMLResponse)
async def account_page(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@router.get("/passport-view", response_class=HTMLResponse)
async def passport_view_page(request: Request):
    return templates.TemplateResponse("passport_view.html", {"request": request})


@router.get("/nhs-nav", response_class=HTMLResponse)
async def nhs_nav_page(request: Request):
    return templates.TemplateResponse("nhs_nav.html", {"request": request})
