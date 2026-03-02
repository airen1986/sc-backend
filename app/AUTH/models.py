from pydantic import BaseModel, EmailStr

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

class SignupPayload(BaseModel):
    name: str
    email: EmailStr
    password: str

class ForgotPasswordPayload(BaseModel):
    email: EmailStr

class ResetPasswordPayload(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str

class ChangePasswordPayload(BaseModel):
    current_password: str
    new_password: str

class ResetPasswordCombinedPayload(BaseModel):
    reset_token: str
    new_password: str
