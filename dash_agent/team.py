from agno.team import Team
from dash_agent.agents.analyst import get_analyst_agent
from dash_agent.agents.engineer import get_engineering_agent
from dash_agent.agents.utils import get_model
from dash_agent.storage import get_agent_db

def get_dash_team():
    analyst = get_analyst_agent()
    engineer = get_engineering_agent()
    
    return Team(
        name="DASH Team",
        model=get_model(),
        members=[analyst, engineer],
        db=get_agent_db(),
        add_history_to_context=True,
        num_history_runs=3,
        add_datetime_to_context=True,
        instructions=[
            "You are the strategic Leader of the DASH Team (Data Agent Self-learning Hub).",
            "Your two members are: Analyst (SQL + insights) and Engineer (dash schema architecture).",
            "Route data questions to the Analyst. Route view/schema creation requests to the Engineer.",
            "If the Analyst fails due to a missing view, ask the Engineer to build it, then retry.",
            "Synthesize member responses into a clear executive summary with insights.",
        ],
        debug_mode=True,
        markdown=True,
        share_member_interactions=True,
    )
