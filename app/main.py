from fastapi import FastAPI, Form, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import hashlib

templates = Jinja2Templates(directory="templates")

app = FastAPI()

SECRET = "SECRET"
manager = LoginManager(SECRET, token_url='/auth/token', use_cookie=True)

# This is a mock user data, replace this with your actual user data
users_db = {
    "johndoe@example.com": {
        "email": "johndoe@example.com",
        "hashed_password": hashlib.sha256("secret".encode()).hexdigest()
    }
}


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@manager.user_loader()
def load_user(email: str):  # could also be an asynchronous function
    user = users_db.get(email)
    return user


@app.post('/auth/token')
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = load_user(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != user['hashed_password']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")

    access_token = manager.create_access_token(
        data=dict(sub=email)
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get("/protected")
def protected_route(user=Depends(manager)):
    return {"user": user}
