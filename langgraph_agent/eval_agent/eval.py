import os

from dotenv import load_dotenv

from langsmith import Client
from langsmith.evaluation import evaluate

from agent import run_agent


load_dotenv()


# --------------------------------------------------
# LangSmith
# --------------------------------------------------

client = Client(
    api_key=os.environ["LANGSMITH_API_KEY"]
)


# --------------------------------------------------
# YOUR EXISTING DATASET
# --------------------------------------------------

DATASET_NAME = "tavily_agent_evaluation_v1"


# --------------------------------------------------
# SIMPLE EVALUATOR
# --------------------------------------------------

def check_tavily_usage(inputs, outputs, reference_outputs):

    expected = reference_outputs

    actual = "tavily" if outputs["used_tavily"] else "none"

    score = 1 if actual == expected else 0

    return {
        "key": "tavily_tool_selection",
        "score": score
    }


# --------------------------------------------------
# RUN EVALUATION
# --------------------------------------------------

results = evaluate(
    run_agent,
    data=DATASET_NAME,
    evaluators=[
        check_tavily_usage
    ],
    experiment_prefix="tavily-langgraph-tool-evaluation"
)


print("\n==============================")
print("EVALUATION COMPLETED")
print("==============================")

print(results)