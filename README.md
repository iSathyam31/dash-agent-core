# 💎 Dash

Dash is an open-source, self-learning data system designed to give your entire team access to a best-in-class data analyst right within Slack or the AgentOS UI. Powered by the **Agno** framework, it bridges the gap between natural language business questions and complex data infrastructure. 

Unlike traditional Text-to-SQL bots that crash when they encounter a schema change, Dash relies on a **dual-tier knowledge and learning system**. The model stays frozen, but the system continuously gets smarter—learning happening entirely in retrieval, not in weights, making it 100% auditable and requiring zero training compute.

---

## 🚀 Key Features & Architecture

### 1. Three Agents, Two Schemas
Dash operates as a coordinated team of three specialists holding strict boundaries over your database schemas:
- **Dash Leader**: The strategic orchestrator. It receives user prompts, delegates tasks, and synthesizes answers. *It cannot touch the database.*
- **Data Analyst**: The SQL expert. Searches the knowledge base, writes, and runs SQL. It connects explicitly with `default_transaction_read_only=on`.
- **Data Engineer**: The infrastructure builder. When the Leader realizes a question is asked often and is too complex, the Engineer builds a view. It can *only* write to the `dash` schema. 

This gives you a hard boundary:
- **`public` schema**: Your company data. You load it. Agents read it. It is untouchable.
- **`dash` schema**: Views, summary tables, computed data. The Engineer owns and maintains it.
- **`ai` schema**: Where Dash stores its sessions, learnings, and knowledge vectors.

### 2. Dual-Tier Knowledge & Self-Learning
- **Context is Everything (Knowledge Base)**: Dash doesn't just guess column meanings. You provide curated JSON knowledge files (`knowledge/tables/`, `knowledge/queries/`, `knowledge/business/`) that define your business rules—like *"ended_at IS NULL means an active subscription"*.
- **The Self-Learning Loop**: Dash captures what it learns automatically. When a user corrects a result or an Analyst fixes a type error, that fix is saved. The next time the question is asked, the Analyst checks the `ai` schema *before* writing SQL. 

### 3. The Autonomous View-Building Loop
When your team repeatedly asks an expensive question (e.g., MRR by plan):
1. The Leader routes to the Engineer.
2. The Engineer creates a pre-optimized view like `dash.monthly_mrr_by_plan`.
3. It calls `update_knowledge` to record this new view in the system.
4. Next time, the Analyst discovers this new view instantly and queries it directly. Faster, pre-validated, and consistent.

---

## 🛠️ Technology Stack
- **Agent Framework**: [Agno](https://github.com/agno-agi/agno).
- **Core LLM**: Defaulting to Azure OpenAI (GPT-4) or standard OpenAI.
- **Memory & Embeddings**: PostgreSQL + PgVector (`ai` schema).
- **Interface**: Runs natively over Slack apps via `@Dash`, or on the web via Streamlit / AgentOS UI.

---

## ⚙️ Setup & Installation Instructions

### 1. Environment Setup
```bash
git clone https://github.com/agno-agi/dash && cd dash
cp example.env .env  # Add your AZURE_OPENAI_API_KEY
docker compose up -d --build
```
*Note: You can run `python scripts/generate_data.py` and `python scripts/load_knowledge.py` inside the container for a synthetic 900-customer demo.*

### 2. Adding Your Own Data (The 5 Steps)
1. **Load tables into `public` schema:** Point Dash at a replica of your data (via pg_dump, Airbyte, etc.).
2. **Add Table Knowledge:** Create JSON definitions for tables explaining their use-cases and quirks inside `knowledge/tables/`.
3. **Add Validated Queries:** Save standard metrics queries into `knowledge/queries/`.
4. **Add Business Rules:** Document gotchas inside `knowledge/business/`.
5. **Load Knowledge:** Run `python scripts/load_knowledge.py` to index those rules into the `ai` vector database.

### 3. Connect to Slack
Dash is meant to live in Slack! Each thread maps to one session, isolating context perfectly.
1. Run Dash and host it publicly (ngrok or deployed domain).
2. Install the Slack app from the manifest in `docs/SLACK_CONNECT`.
3. Add your `SLACK_TOKEN` and `SLACK_SIGNING_SECRET` to `.env`.

---

## 🧪 Evals and Scheduled Tasks

**Built-in Scheduler**
Dash automatically re-indexes your knowledge base every night. You can extend this to pull daily metric summaries, run anomaly detection, or send weekly Slack digests automatically.

**Run Evals**
Test your instance to ensure safety and accuracy before rolling it out to the company:
```bash
python -m evals --category accuracy
python -m evals --category security  # Tests schema boundary enforcement
```

---

## 📚 Blog & Further Reading

> **📖 Read the full technical breakdown by Ashpreet Bedi:** 
> [Dash: The Data Agent Every Company Needs](https://www.ashpreetbedi.com/articles/dash-v2)

This architecture applies **Systems Engineering Principles** across five layers—Agent, Data, Security, Interface, and Infrastructure—ensuring that your data agent is auditable, secure by configuration, and continuously compounding in value.
