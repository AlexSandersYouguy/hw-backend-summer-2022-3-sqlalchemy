from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
import base64

password_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:   
        password_hasher.verify(hashed, password)
        return True
    except (VerifyMismatchError, VerificationError):
        return False
    

def int_id_generator():
    cnt = 2
    while True:
        yield cnt
        cnt += 1
gen = int_id_generator()