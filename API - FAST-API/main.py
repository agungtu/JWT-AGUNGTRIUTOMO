
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext



# SILAHKAN DI CLONE DAN DI RUN UNTUK MENCOBA API INI. JANGAN LUPA UNTUK MENGGANTI SECRET_KEY DENGAN KEY YANG LEBIH AMAN.
#SAYA AKAN CEK DIPERTEMUAN SELANJUTNYA DAN SAYA BERHARAP SEMUA SUDAH BISA MENGGUNAKAN FASTAPI DAN JWT UNTUK AUTENTIKASI DAN CRUD.
# FASTAPI
app = FastAPI(
    title="FastAPI CRUD + JWT",
    version="1.0.0"
)
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# JWT CONFIGURATION
SECRET_KEY = "rahasia_super_aman_ganti_dengan_key_acak"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# PASSWORD HASH
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
# HTTP BEARER
security = HTTPBearer()
# MODEL DATA
class Item(BaseModel):
    name: Optional[str] = None
    Umur: Optional[int] = None
    description: Optional[str] = None
    price: Optional[float] = None
# MODEL LOGIN
class LoginRequest(BaseModel):
    username: str
    password: str
#Jika ingin mendapatkan hashed password bcrypt dari password seperti agung123, Anda bisa menggunakan Python dengan library bcrypt.
#pip install bcrypt
ppwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

password = "agung123"

hashed = pwd_context.hash(password)

print("Password :", password)
print("Hash     :", hashed)

print(
    "Verifikasi :",
    pwd_context.verify(password, hashed)
)
# SIMULASI DATABASE USER
users_db = {
    "admin": {
        "username": "admin",
        # Password: agung123
        #hashed password dihasilkan dari bcrypt hash
        "hashed_password": 
            "$2b$12$CIbJ.ODZfx3Q/iimd6jhaOZWTrlcRjfR2ZHGe2GaW1Jkksl2BhOXq",
        "role": "admin",
    }
}
# SIMULASI DATABASE ITEM

items_db = {}
# VERIFY PASSWORD
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    try:
        return pwd_context.verify(
            plain_password,
            hashed_password
        )
    except Exception:
        return False
    
# CREATE JWT TOKEN
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc)
        +
        (
            expires_delta
            or timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )
    )
    to_encode.update({
        "exp": expire
    })
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt
# GET CURRENT USER

# GET CURRENT USER
def get_current_user(
    credentials: HTTPAuthorizationCredentials =
        Depends(security)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau telah kedaluwarsa.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        role = payload.get("role")

        if not username or not role:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = users_db.get(username)

    if user is None:
        raise credentials_exception

    return user
# ROOT
@app.get("/")
async def root():
    return {
        "message": "FastAPI CRUD API is running",
        "authentication": "JWT",
    }
# LOGIN
@app.post("/login")
async def login(
    request: LoginRequest
):
    user = users_db.get(
        request.username
    )
    # Username tidak ditemukan
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Username atau password salah",
        )
    # Cek password
    password_valid = verify_password(
        request.password,
        user["hashed_password"]
    )
    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Username atau password salah",
        )
    # Generate JWT
    access_token = create_access_token({
        "sub":
            user["username"],
        "role":
            user["role"],
    })
    return {
        "access_token":
            access_token,
        "token_type":
            "bearer",
    }
# CEK USER LOGIN
@app.get("/me")
async def get_me(
    current_user: dict =
        Depends(get_current_user)

):
    return {
        "username":
            current_user["username"],
        "role":
            current_user["role"],
    }
# CREATE - POST
# WAJIB JWT SUDAH LOGIN
@app.post("/items/{item_id}")
async def create_item(
    item_id: int,
    item: Item,
    current_user: dict =
        Depends(get_current_user)
):
    if item_id in items_db:
        raise HTTPException(
            status_code=409,
            detail="Item already exists"
        )
    items_db[item_id] = item.model_dump()
    return {
        "message":
            f"Item created successfully by "
            f"{current_user['username']}",

        "item":
            items_db[item_id],
    }
# READ - GET
# TIDAK WAJIB JWT
@app.get("/items/{item_id}")
async def read_item(
    item_id: int
):
    if item_id not in items_db:
        raise HTTPException(
            status_code=404,
            detail="Item nggak Ada"
        )
    return {
        "item_id":
            item_id,
        "item":
            items_db[item_id],
    }
# UPDATE - PUT
# WAJIB JWT
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    current_user: dict =
        Depends(get_current_user)
):
    if item_id not in items_db:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    items_db[item_id] = item.model_dump()
    return {
        "message":
            f"Item updated successfully by "
            f"{current_user['username']}",
        "item":
            items_db[item_id],
    }
# DELETE
# WAJIB JWT
@app.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    current_user: dict =
        Depends(get_current_user)
):
    if item_id not in items_db:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    deleted_item = items_db.pop(
        item_id
    )
    return {
        "message":
            f"Item deleted successfully by "
            f"{current_user['username']}",

        "deleted_item":
            deleted_item,
    }

#pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]