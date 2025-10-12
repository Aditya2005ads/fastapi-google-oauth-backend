from dotenv import load_dotenv, find_dotenv
import os
_env_set = load_dotenv(find_dotenv(".env"))
if not _env_set:
    print("No settings file found trying to load example env file")
    load_dotenv(find_dotenv(".env.example"))

    
class Config:
    def __init__(self) -> None:
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretjwt")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
settings = Config()