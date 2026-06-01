import re
from typing import List, Dict, Any

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger


class ReActAgent:
    def __init__(
        self,
        llm: LLMProvider,
        tools: List[Dict[str, Any]],
        max_steps: int = 5
    ):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        System prompt hướng dẫn mô hình làm việc theo ReAct.
        """

        tool_descriptions = "\n".join(
            [
                f"- {tool['name']}: {tool['description']}"
                for tool in self.tools
            ]
        )

        return f"""You are a ReAct Agent that solves problems step by step using tools.

Available tools:
{tool_descriptions}

STRICT OUTPUT FORMAT — generate ONLY ONE step per response:

If you need to call a tool:
Thought: <your reasoning>
Action: tool_name(arguments)

If you have enough information to answer:
Thought: <your reasoning>
Final Answer: <your answer>

CRITICAL RULES:
- Generate ONLY ONE Thought + ONE Action per response, then STOP.
- Do NOT write "Observation:" — the system provides observations automatically.
- Do NOT hallucinate or invent tool results.
- Do NOT simulate multiple steps in a single response.
- Only write "Final Answer:" when you actually have real data from tool calls.
"""

    def run(self, user_input: str) -> str:
        logger.log_event(
            "AGENT_START",
            {
                "input": user_input,
                "model": self.llm.model_name
            }
        )

        scratchpad = ""
        steps = 0

        while steps < self.max_steps:

            prompt = f"""
User Question:
{user_input}

{scratchpad}
"""

            result = self.llm.generate(
                prompt,
                system_prompt=self.get_system_prompt()
            )

            content = result["content"]

            logger.log_event(
                "LLM_RESPONSE",
                {
                    "step": steps,
                    "response": content
                }
            )

            # ==========================
            # 1. Check Final Answer
            # ==========================
            final_match = re.search(
                r"Final Answer:\s*(.*)",
                content,
                re.DOTALL
            )

            if final_match:
                final_answer = final_match.group(1).strip()

                logger.log_event(
                    "AGENT_FINAL_ANSWER",
                    {"answer": final_answer}
                )

                return final_answer

            # ==========================
            # 2. Parse Action
            # ==========================
            action_match = re.search(
                r"Action:\s*(\w+)\((.*?)\)",
                content,
                re.DOTALL
            )

            if not action_match:
                logger.error(
                    f"Cannot parse Action from:\n{content}"
                )
                return "Failed to parse agent action."

            tool_name = action_match.group(1).strip()
            args = action_match.group(2).strip()

            # ==========================
            # 3. Execute Tool
            # ==========================
            observation = self._execute_tool(
                tool_name,
                args
            )

            logger.log_event(
                "TOOL_EXECUTION",
                {
                    "tool": tool_name,
                    "args": args,
                    "observation": observation
                }
            )

            # ==========================
            # 4. Update scratchpad
            # ==========================
            scratchpad += (
                f"\n{content}"
                f"\nObservation: {observation}\n"
            )

            steps += 1

        logger.log_event(
            "AGENT_END",
            {"steps": steps}
        )

        return "Maximum reasoning steps reached."

    def _execute_tool(
        self,
        tool_name: str,
        args: str
    ) -> str:
        """
        Execute tool dynamically.
        """

        for tool in self.tools:

            if tool["name"] == tool_name:

                try:
                    func = tool["function"]

                    result = func(args)

                    return str(result)

                except Exception as e:

                    logger.error(
                        f"Tool execution failed: {e}"
                    )

                    return f"Tool Error: {str(e)}"

        return f"Tool '{tool_name}' not found."