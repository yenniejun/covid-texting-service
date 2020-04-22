# settings.py
from dotenv import load_dotenv
load_dotenv(verbose=True)

import os
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")