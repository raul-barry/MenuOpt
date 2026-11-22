from pydantic import BaseModel, Field


class DispositivoPushRegistro(BaseModel):
    id_instalacion: str = Field(min_length=16, max_length=80)
    token: str = Field(min_length=20, max_length=4096)
    plataforma: str = Field(default="ANDROID", pattern="^(ANDROID|IOS|WEB)$")


class DispositivoPushRevocar(BaseModel):
    id_instalacion: str = Field(min_length=16, max_length=80)


class DispositivoPushRespuesta(BaseModel):
    registrado: bool
