"""
Chatbot Baseline — Lab 3
A simple LLM chatbot with NO tools and NO agentic loop.
Purpose: demonstrate limitations vs ReAct agent on multi-step tasks.
"""

from src.core.provider_factory import create_provider
from src.telemetry.logger import logger

SYSTEM_PROMPT = """You are a helpful e-commerce assistant.
Answer customer questions about products, pricing, discounts, and shipping.
Be concise and direct."""

TEST_CASES = [
    "How much does an iPhone cost?",
    "I want to buy 2 iPhones using coupon code 'WINNER' and ship to Hanoi. What is the total price?",
    "Is the iPad Pro in stock?",
    "What is 15% off of $1998 plus a $7 shipping fee?",
]


class Chatbot:
    def __init__(self):
        self.llm = create_provider()
        self.history: list[dict] = []
        print(f"[Chatbot] Provider: {self.llm.model_name}\n")

    def chat(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})

        # Build full conversation as a single prompt
        conversation = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in self.history
        )

        result = self.llm.generate(conversation, system_prompt=SYSTEM_PROMPT)
        answer = result["content"]

        self.history.append({"role": "assistant", "content": answer})

        logger.log_event("CHATBOT_TURN", {
            "input": user_input,
            "output": answer,
            "latency_ms": result["latency_ms"],
            "tokens": result.get("usage", {}),
        })

        return answer


def run_interactive():
    bot = Chatbot()
    print("=== Chatbot Baseline (type 'quit' to exit) ===\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue
        response = bot.chat(user_input)
        print(f"Bot: {response}\n")


def run_test_cases():
    bot = Chatbot()
    print("=== Chatbot Baseline — Automated Test Cases ===\n")
    for i, question in enumerate(TEST_CASES, 1):
        print(f"[Test {i}] {question}")
        response = bot.chat(question)
        print(f"Answer: {response}")
        print("-" * 60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_test_cases()
    else:
        run_interactive()
