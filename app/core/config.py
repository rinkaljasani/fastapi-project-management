import os


class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-me")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
settings = Settings()
