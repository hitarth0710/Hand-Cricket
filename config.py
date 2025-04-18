import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GAME_TIMEOUT = 3  # Time in seconds to show hand