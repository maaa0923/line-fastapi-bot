from dotenv import load_dotenv
import os

load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/credentials.json"

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")