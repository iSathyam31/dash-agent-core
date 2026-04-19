from agno.agent import Agent
from agno.tools.sql import SQLTools
from dash_agent.agents.utils import get_model, get_db_url
from dash_agent.storage import get_agent_db, get_dash_knowledge, get_learning_machine
import os

def get_engineering_agent():
    # Read modular context
    base_path = os.path.dirname(os.path.dirname(__file__))
    tables_path = os.path.join(base_path, "knowledge", "tables")
    table_context = ""
    for file in sorted(os.listdir(tables_path)):
        if file.endswith(".json"):
            table_context += open(os.path.join(tables_path, file)).read() + "\n"

    return Agent(
        name="Engineer",
        role="Schema management, view creation, optimised data storage in the dash schema",
        model=get_model(),
        db=get_agent_db(),
        knowledge=get_dash_knowledge(),
        search_knowledge=True,
        learning=get_learning_machine(),
        add_learnings_to_context=True,
        add_history_to_context=True,
        num_history_runs=3,
        add_datetime_to_context=True,
        tools=[
            SQLTools(db_url=get_db_url()),
        ],
        instructions=[
            "You are a Senior Data Engineer specializing in database architecture and self-learning systems.",
            "You have full DDL/DML permission scoped to the 'dash' schema ONLY.",
            "You can READ from 'ecommerce' for raw data, but all WRITES go into 'dash'.",
            "Your goal: create views, summary tables, and computed metrics that the Analyst can reuse.",
            "Refer to the 'ecommerce' schema based on these Table Definitions:",
            table_context,
            "When you create a new view or table, record its purpose in the knowledge base.",
        ],
        debug_mode=True,
        markdown=True,
    )
