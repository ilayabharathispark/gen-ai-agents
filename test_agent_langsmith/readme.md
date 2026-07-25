# Google ADK Agent with LangSmith Observability

A production-ready Google ADK Agent integrated with LangSmith for AI observability and deployable on Google Cloud Run.
langsmith : https://smith.langchain.com/
---

# Architecture

```
                User
                  │
                  ▼
            Google ADK Agent
                  │
      ┌───────────┴────────────┐
      │                        │
      ▼                        ▼
   Custom Tools             Gemini/Groq
      │
      ▼
  Business Logic

      │
      ▼
 LangSmith Tracing

      │
      ▼
 Google Cloud Run
```

---

# Project Structure

```
test_agent_langsmith/
│
├── __init__.py
├── agent.py
├── observability.py
├── .env
├── requirements.txt
├── Dockerfile
└── README.md
```

---

# File Explanation

## agent.py

This is the main agent.

Responsibilities:

- Creates the ADK Agent
- Registers tools
- Defines the model
- Defines the system instruction

Example:

```python
root_agent = Agent(
    ...
)
```

This file contains only the AI logic.

---

## observability.py

Responsible for enabling LangSmith tracing.

Example

```python
from dotenv import load_dotenv
load_dotenv()

from langsmith.integrations.google_adk import configure_google_adk

configure_google_adk()
```

This initializes LangSmith before the agent starts.

Without this file:

- prompts are NOT traced
- tool calls are NOT visible
- execution graph is NOT visible

---

## __init__.py

Exports the root agent.

```python
from .agent import root_agent
```

ADK looks for this file while loading agents.

---

## .env

Contains environment variables.

Example

```
LANGSMITH_API_KEY=xxxx

LANGSMITH_TRACING=true

LANGSMITH_PROJECT=Demo Agent

LANGSMITH_ENDPOINT=https://api.smith.langchain.com

```

Never commit this file.

---

## requirements.txt

Contains Python dependencies.

Example

```
google-adk

langsmith

python-dotenv

etc...
```

Install using

```
pip install -r requirements.txt
```

---

## Dockerfile

Creates the production container.

Example

```
FROM python:3.12-slim

COPY .

RUN pip install -r requirements.txt

CMD ...
```

This image is deployed to Cloud Run.

---

# Running Locally

Go to the parent directory

```
my-ai-agents/test_agent_langsmith/
```

Run

```
adk web
```

Open

```
http://127.0.0.1:8000
```

---

# LangSmith Integration

LangSmith provides AI observability.

It captures

- Prompt
- Response
- Agent execution
- Tool calls
- Latency
- Token usage
- Errors

Without LangSmith

You only know

"Agent failed"

With LangSmith

You know

- Which prompt was sent
- Which tool executed
- How long it took
- Why it failed

---

# Deploying to Cloud Run

Build

```
gcloud builds submit \
--tag asia-south1-docker.pkg.dev/ilaya-bharathi-murugan/agent/demo-agent
```

Deploy

```
gcloud run deploy demo-agent \
--image asia-south1-docker.pkg.dev/ilaya-bharathi-murugan/agent/demo-agent \
--region asia-south1 \
--allow-unauthenticated \
--set-env-vars \
LANGSMITH_API_KEY=lsv2_xxxxxxxxx,\
LANGSMITH_PROJECT=DemoAgent,\
LANGSMITH_TRACING=true,\
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

Set environment variables

```
LANGSMITH_API_KEY

LANGSMITH_TRACING

LANGSMITH_PROJECT

LANGSMITH_ENDPOINT
```

Cloud Run automatically injects them into the container.

---

# Do we still need LangSmith if deployed on Cloud Run?

Yes.

Cloud Run only provides infrastructure monitoring.

It does NOT understand AI workflows.

Cloud Run tells you

- CPU
- Memory
- HTTP Requests
- Container Logs

LangSmith tells you

- Prompt
- Response
- Tool Calls
- Agent Graph
- Token Usage
- Execution Flow

These solve different problems.

---

# Do we need Google Cloud Logging?

Yes.

Recommended production stack

Cloud Logging

Purpose

- Application logs
- Exceptions
- HTTP logs

---

Cloud Monitoring

Purpose

- CPU
- Memory
- Request latency

---

Cloud Trace

Purpose

- Distributed tracing
- End-to-end request timeline

---

LangSmith

Purpose

- AI observability
- Prompt inspection
- Tool execution
- Agent execution graph

---

# Recommended Production Architecture

```
                User
                  │
                  ▼
             Cloud Run
                  │
          Google ADK Agent
                  │
       ┌──────────┴──────────┐
       │                     │
       ▼                     ▼
   LangSmith          Cloud Logging
       │
       ▼
Cloud Trace (OpenTelemetry)
```

---

# Should we integrate LangGraph?

No.

Google ADK already provides

- Agents
- Tools
- Multi-agent workflows
- Sessions
- Memory

LangGraph is another orchestration framework.

Using both in the same project generally adds unnecessary complexity unless you have a specific reason.

---

# Future Enhancements

- Qdrant RAG Tool
- MCP Server Integration
- Google Search Tool
- BigQuery Tool
- Gmail Tool
- Cloud Trace (OpenTelemetry)
- Human-in-the-loop workflows
- Evaluation datasets in LangSmith

---

# Conclusion

This project demonstrates a production-ready Google ADK agent with:

- Google ADK
- LangSmith Observability
- Custom Tools
- Cloud Run Deployment
- Docker
- Environment-based Configuration

It serves as a strong foundation for building scalable AI agents on Google Cloud.
