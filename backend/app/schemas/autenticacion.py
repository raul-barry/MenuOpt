from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegistroUsuarioSchema(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=100, description="Nombres del usuario")
    apellidos: str = Field(..., min_length=2, max_length=100, description="Apellidos del usuario")
    correo: EmailStr = Field(..., description="Correo electrónico único del usuario")
    contrasena: str = Field(..., min_length=8, description="Contraseña segura (mínimo 8 caracteres)")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto opcional")

    @field_validator("correo", mode="before")
    @classmethod
    def normalizar_correo(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("nombres", "apellidos", mode="before")
    @classmethod
    def limpiar_texto(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v


class LoginSchema(BaseModel):
    correo: EmailStr = Field(..., description="Correo electrónico del usuario")
    contrasena: str = Field(..., min_length=1, description="Contraseña del usuario")

    @field_validator("correo", mode="before")
    @classmethod
    def normalizar_correo(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v
