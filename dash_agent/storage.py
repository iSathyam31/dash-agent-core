import os
from dotenv import load_dotenv
from agno.db.postgres import PostgresDb
from agno.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from agno.knowledge.embedder.azure_openai import AzureOpenAIEmbedder

load_dotenv()

def get_pgvector_db_url():
    """SQLAlchemy-compatible URL for PgVector (requires psycopg driver)."""
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    host = os.getenv("PGHOST")
    port = os.getenv("PGPORT", 5432)
    database = os.getenv("PGDATABASE")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"


def get_embedder():
    """Azure OpenAI Embedder for vectorizing knowledge."""
    return AzureOpenAIEmbedder(
        id=os.getenv("EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
        api_key=os.getenv("EMBEDDING_API_KEY"),
        azure_endpoint=os.getenv("EMBEDDING_ENDPOINT"),
        api_version=os.getenv("EMBEDDING_API_VERSION", "2024-02-01"),
    )


def get_agent_db():
    """PostgresDb for persisting agent run history and sessions."""
    return PostgresDb(
        db_url=get_pgvector_db_url(),
        db_schema="dash"
    )


def get_dash_knowledge():
    """Static, curated knowledge store — table schemas, validated SQL, business rules."""
    return Knowledge(
        vector_db=PgVector(
            table_name="dash_knowledge",
            db_url=get_pgvector_db_url(),
            schema="dash",
            embedder=get_embedder(),
        ),
    )


def get_dash_learnings():
    """Dynamic, discovered knowledge — error patterns, user corrections, query learnings."""
    return Knowledge(
        vector_db=PgVector(
            table_name="dash_learnings",
            db_url=get_pgvector_db_url(),
            schema="dash",
            embedder=get_embedder(),
        ),
    )


def get_learning_machine():
    """LearningMachine in AGENTIC mode — agent decides when and what to learn."""
    return LearningMachine(
        knowledge=get_dash_learnings(),
        learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC),
    )
