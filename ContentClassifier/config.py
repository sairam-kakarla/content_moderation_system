import os
from dotenv import load_dotenv
config_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(config_directory, ".env")
load_dotenv(dotenv_path=dotenv_path)
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("Error: GOOGLE_API_KEY is missing from the .env file in the config directory.")