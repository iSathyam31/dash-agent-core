from agno.agent import Agent
from agno.tools.sql import SQLTools
from dash_agent.agents.utils import get_model, get_db_url
from dash_agent.storage import get_agent_db, get_dash_knowledge, get_learning_machine
import os

def get_analyst_agent():
    # Read modular context
    base_path = os.path.dirname(os.path.dirname(__file__))
    metrics = open(os.path.join(base_path, "knowledge", "metrics.json")).read()
    examples = open(os.path.join(base_path, "knowledge", "examples.sql")).read()
    
    # Load all table definitions
    tables_path = os.path.join(base_path, "knowledge", "tables")
    table_context = ""
    for file in sorted(os.listdir(tables_path)):
        if file.endswith(".json"):
            table_context += open(os.path.join(tables_path, file)).read() + "\n"

    return Agent(
        name="Analyst",
        role="SQL generation, execution, schema introspection, data quality handling",
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
            "You are a Senior Data Analyst specialized in E-commerce insights.",
            "You have access to two schemas: 'ecommerce' (raw data) and 'dash' (learned insights).",
            "--- STRATEGIC PRIORITY ---",
            "Always check the 'dash' schema FIRST for pre-built views and summaries before querying raw 'ecommerce' data.",
            "-------------------------",
            "Use the following Table Definitions to understand the database structure:",
            table_context,
            "Use the following Metrics Definitions for KPI calculations:",
            metrics,
            "Use these SQL Examples as high-quality grounding for your queries:",
            examples,
            "Fix any SQL errors by inspecting the schema and retrying.",
            "Provide insightful analysis, not just raw data.",
        ],
        debug_mode=True,
        markdown=True,
    )
