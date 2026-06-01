"""
ReAct Agent Runner — Lab 3
Runs the ReAct agent with e-commerce tools.
Compare outputs against chatbot.py to see the difference.
"""

from src.core.provider_factory import create_provider
from src.agent.agent import ReActAgent
from src.agent.agent_v2 import ReActAgentV2
from src.tools import ALL_TOOLS

TEST_CASES = [
    "How much does an iPhone cost?",
    "I want to buy 2 iPhones using coupon code 'WINNER' and ship to Hanoi. What is the total price?",
    "Is the iPad Pro in stock?",
    "What is 15% off of $1998 plus a $7 shipping fee?",
]


def _make_agent(version: str):
    llm = create_provider()
    if version == "v2":
        return ReActAgentV2(llm=llm, tools=ALL_TOOLS, max_steps=8), llm.model_name
    return ReActAgent(llm=llm, tools=ALL_TOOLS, max_steps=8), llm.model_name


def run_interactive(version: str = "v1"):
    agent, model = _make_agent(version)
    print(f"=== ReAct Agent {version.upper()} (type 'quit' to exit) ===")
    print(f"Provider: {model} | Tools: {[t['name'] for t in ALL_TOOLS]}\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue
        response = agent.run(user_input)
        print(f"Agent: {response}\n")


def run_test_cases(version: str = "v1"):
    agent, model = _make_agent(version)
    print(f"=== ReAct Agent {version.upper()} — Automated Test Cases ===")
    print(f"Provider: {model}\n")

    for i, question in enumerate(TEST_CASES, 1):
        print(f"[Test {i}] {question}")
        response = agent.run(question)
        print(f"Answer: {response}")
        print("-" * 60)


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    version = "v2" if "v2" in args else "v1"
    if "test" in args:
        run_test_cases(version)
    else:
        run_interactive(version)
