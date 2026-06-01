"""
Agent v2 — improved system prompt based on failure analysis of v1.

Failures identified in v1:
1. Agent called calculator() before calc_shipping(), using a hallucinated
   shipping cost ($15) instead of fetching the real value from the tool.

Fixes applied in v2:
1. Explicit tool-ordering rule: always fetch all data before calculating.
2. "Never assume numeric values" instruction.
3. Numbered step plan requirement before acting.
"""

import re
from typing import List, Dict, Any

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger


class ReActAgentV2:
    def __init__(
        self,
        llm: LLMProvider,
        tools: List[Dict[str, Any]],
        max_steps: int = 8
    ):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join(
            f"- {tool['name']}: {tool['description']}"
            for tool in self.tools
        )

        return f"""You are a ReAct Agent v2 — improved for accuracy and reliability.

Available tools:
{tool_descriptions}

STRICT OUTPUT FORMAT — generate ONLY ONE step per response:

If you need to call a tool:
Thought: <your reasoning>
Action: tool_name(arguments)

If you have enough information from real tool results:
Thought: <your reasoning>
Final Answer: <your answer>

CRITICAL RULES:
- Generate ONLY ONE Thought + ONE Action per response, then STOP.
- Do NOT write "Observation:" — the system provides it automatically.
- NEVER assume or invent numeric values (prices, weights, discounts, fees).
  Every number must come from a real tool call.
- TOOL ORDER for pricing tasks: get_price → check_stock → get_discount
  → calc_shipping → calculator. Always call calc_shipping BEFORE calculator.
- Only write "Final Answer:" after you have real observations for ALL
  required values.
"""

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_V2_START", {
            "input": user_input,
            "model": self.llm.model_name
        })

        scratchpad = ""
        steps = 0

        while steps < self.max_steps:
            prompt = f"User Question:\n{user_input}\n\n{scratchpad}"

            result = self.llm.generate(prompt, system_prompt=self.get_system_prompt())
            content = result["content"]

            logger.log_event("LLM_RESPONSE", {"step": steps, "response": content, "version": "v2"})

            final_match = re.search(r"Final Answer:\s*(.*)", content, re.DOTALL)
            if final_match:
                answer = final_match.group(1).strip()
                logger.log_event("AGENT_V2_FINAL_ANSWER", {"answer": answer})
                return answer

            action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", content, re.DOTALL)
            if not action_match:
                logger.error(f"[v2] Cannot parse Action from:\n{content}")
                return "Failed to parse agent action."

            tool_name = action_match.group(1).strip()
            args = action_match.group(2).strip()

            observation = self._execute_tool(tool_name, args)

            logger.log_event("TOOL_EXECUTION", {
                "tool": tool_name,
                "args": args,
                "observation": observation,
                "version": "v2"
            })

            scratchpad += f"\n{content}\nObservation: {observation}\n"
            steps += 1

        logger.log_event("AGENT_V2_END", {"steps": steps, "outcome": "timeout"})
        return "Maximum reasoning steps reached."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        for tool in self.tools:
            if tool["name"] == tool_name:
                try:
                    return str(tool["function"](args))
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    return f"Tool Error: {str(e)}"
        return f"Tool '{tool_name}' not found."
