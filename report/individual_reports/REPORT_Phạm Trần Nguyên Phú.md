# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [Your Name Here]
- **Student ID**: [Your ID Here]
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

### Modules Implemented

| Module | Role |
| :--- | :--- |
| `src/tools/check_stock.py` | Tool: returns stock quantity and unit weight (kg) |
| `src/tools/get_price.py` | Tool: returns current price in USD per unit |
| `src/tools/get_discount.py` | Tool: maps coupon code → discount percentage |
| `src/tools/calc_shipping.py` | Tool: computes shipping fee by weight + destination city |
| `src/tools/calculator.py` | Tool: safe AST-based arithmetic evaluator |
| `src/tools/__init__.py` | Exports `ALL_TOOLS` list in agent-compatible format |
| `src/agent/agent_v2.py` | `ReActAgentV2` class with improved system prompt |
| `chatbot.py` | Chatbot baseline — interactive + test mode |
| `agent.py` | Agent runner — supports v1/v2, interactive/test mode |
| `analyze_logs.py` | Log parser: detects hallucination patterns, prints performance report |

### Code Highlights

**Tool interface contract** — all tools follow the same signature so `ALL_TOOLS` is plug-and-play:

```python
# src/tools/__init__.py
ALL_TOOLS = [
    {"name": "check_stock",   "description": "...", "function": check_stock},
    {"name": "get_price",     "description": "...", "function": get_price},
    {"name": "get_discount",  "description": "...", "function": get_discount},
    {"name": "calc_shipping", "description": "...", "function": calc_shipping},
    {"name": "calculator",    "description": "...", "function": calculator},
]
```

**Safe math evaluator** — uses `ast.parse` + recursive node evaluation instead of `eval()`:

```python
# src/tools/calculator.py
def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")
```

**Hallucination detection in log analyzer** — flags `calculator` called before `calc_shipping`:

```python
# analyze_logs.py
if data.get("tool") == "calculator":
    if "calc_shipping" not in current["tools_called"][:-1]:
        current["hallucination_flags"].append(
            f"Step {current['steps']}: calculator called before calc_shipping"
        )
```

### How my code interacts with the ReAct loop

Each tool is called by name inside `_execute_tool()` in the agent. The agent extracts
`tool_name` and `args` from the LLM's `Action: tool_name(args)` output via regex, then
dispatches to the matching function in `ALL_TOOLS`. The tool's return value becomes the
`Observation` appended to the scratchpad for the next LLM iteration.

---

## II. Debugging Case Study (10 Points)

### Problem: Agent Hallucinated Shipping Cost Without Calling the Tool

**Input**: `"I want to buy 2 iPhones using coupon code 'WINNER' and ship to Hanoi. What is the total price?"`

**Log Source**: `logs/2026-06-01.log` — event at step 3 (timestamp `08:33:46`):

```json
{
  "event": "LLM_RESPONSE",
  "data": {
    "step": 2,
    "response": "Thought: I've already calculated the total weight for shipping (0.8 kg) and the shipping cost ($15).\nAction: calculator('999 * 2 * 0.9 + 15')"
  }
}
```

The agent skipped `calc_shipping` entirely and assumed a $15 shipping fee, then called
`calculator` with that fabricated value.

**Diagnosis**: The v1 system prompt only said *"do not write Observation"* but did not
forbid the agent from *using assumed values* in arguments. The LLM's training data
includes many e-commerce examples where international shipping costs ~$15, so it
pattern-matched to that prior knowledge rather than fetching the real value.

This is **parametric knowledge leakage**: the model substituted a memorized value for a
required tool call. The scratchpad at that point had: `get_price → check_stock → get_discount`
completed but `calc_shipping` missing — the agent implicitly assumed it already knew the answer.

**Solution — Agent v2 system prompt additions**:

```
TOOL ORDER for pricing tasks: get_price → check_stock → get_discount
  → calc_shipping → calculator. Always call calc_shipping BEFORE calculator.

NEVER assume or invent numeric values (prices, weights, discounts, fees).
Every number must come from a real tool call.
```

**Result**: In v2 logs (session 2), the agent correctly called `calc_shipping('0.8, Hanoi')`
at step 3, received `$7.00` from the tool, and used that real value in the final calculation:
`999 * 2 * 0.9 + 7 = 1805.2`. Average latency dropped from 15,865ms (v1) to the same
correct answer with no wasted self-correction steps.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. How did the `Thought` block help?

The `Thought` block forces the model to externalize its reasoning **before** committing to
an action. In chatbot mode, the model jumps straight to generating an answer from parametric
memory — it cannot pause and say "wait, I need to look this up." In agent mode, the Thought
acts as a planning step: `"I need the price first, then check discount, then shipping"`.

This is why the chatbot answered the iPhone price question with *"Depends on the model — could
be $799–$1,299"* (parametric hedging), while the agent answered *"$999"* (one real tool call).

### 2. When did the Agent perform *worse* than the Chatbot?

**Test case 4**: `"What is 15% off of $1998 plus a $7 shipping fee?"` — the chatbot answered
correctly ($1,705.30) in a single response. The agent took 2–4 steps, calling `get_discount`
unnecessarily (it tried to look up a coupon code even though the question gave the percentage
directly), and sometimes hit the calculator regex bug.

**Key insight**: The ReAct loop adds overhead for tasks where all required values are
already present in the question. A chatbot is optimal for pure arithmetic with no missing
data. An agent pays a latency cost (one LLM call per step + tool execution) that is only
justified when external data retrieval is needed.

### 3. How did Observations influence next steps?

The `Observation` is the grounding signal. Without it, the LLM hallucinates (as seen in v1
step 3). With it, the scratchpad grows into a structured fact sheet:

```
Observation: iPhone price is $999 per unit.
Observation: iPhone - 5 units in stock. Weight: 0.4 kg per unit.
Observation: WINNER coupon gives 10% discount.
Observation: Shipping to Hanoi for 0.8 kg: $7.00
```

Each Observation narrows the remaining uncertainty. By step 5, the agent has all four
values and can call `calculator` with no invention required. The Observation loop is
essentially **Retrieval-Augmented Reasoning** — instead of one big RAG retrieval, the agent
retrieves incrementally, guided by its own Thought.

---

## IV. Future Improvements (5 Points)

### Scalability

The current single-threaded ReAct loop is sequential: each tool call blocks the next. For
independent data fetches (price + stock + discount can all be queried in parallel),
a **parallel tool-call architecture** (as in OpenAI's tool_choice with multiple function
calls) would reduce latency proportionally. LangGraph supports parallel edges for this.

For many-tool systems (50+ tools), the agent would need **tool retrieval**: embed tool
descriptions in a vector DB and retrieve only the top-k relevant tools per question, keeping
the context window manageable.

### Safety

Add a **Supervisor LLM** layer that audits the agent's plan before execution — specifically
checking that argument values are grounded in prior Observations and not invented. This
catches hallucination at planning time rather than after a wasted tool call.

For tools with real side effects (database writes, order placement), add a **confirmation
step** where the agent must output a structured JSON plan that a rule-based validator
approves before execution.

### Performance

Replace the regex action parser with a **structured output** approach: instruct the LLM
to output a JSON object `{"thought": "...", "action": {"tool": "...", "args": "..."}}`,
then parse with `json.loads()`. This eliminates the nested-parentheses regex bug entirely
and makes action parsing deterministic.

Track **token cost per session** in `analyze_logs.py` using the `LLM_METRIC` events already
logged by `PerformanceTracker`, and add a cost budget guardrail (`max_cost_usd` per session)
to prevent runaway billing in production.

---

> [!NOTE]
> Rename this file to `REPORT_[YOUR_NAME].md` before final submission.
