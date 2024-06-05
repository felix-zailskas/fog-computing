import os

from dotenv import load_dotenv

load_dotenv()

GCLOUD_SERVICE_ACCOUNT_KEY = os.getenv("GCLOUD_SERVICE_ACCOUNT_KEY")
GCLOUD_SERVICE_ACCOUNT_KEY_ID = os.getenv("GCLOUD_SERVICE_ACCOUNT_KEY_ID")
