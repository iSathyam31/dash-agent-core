import os
from agno.models.azure import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_model():
    return AzureOpenAI(
        id=os.getenv("AZURE_DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    )

def get_db_url():
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    host = os.getenv("PGHOST")
    port = os.getenv("PGPORT", 5432)
    database = os.getenv("PGDATABASE")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"
