"""LLM access layer: litellm-backed client, mock clients for offline runs,
budget fuses and retry with exponential backoff."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass

GLOBAL_BUDGET_USD = 220.0


class BudgetExceeded(Exception):
    pass


@dataclass
class LLMReply:
    text: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_s: float
    error: str | None = None


class BudgetTracker:
    """Accumulates spend into api_usage.jsonl; trips at run/global caps."""

    def __init__(self, usage_path: str, run_cap_usd: float | None = None,
                 global_cap_usd: float = GLOBAL_BUDGET_USD):
        self.usage_path = usage_path
        self.run_cap = run_cap_usd
        self.global_cap = global_cap_usd
        self.run_total = 0.0
        self.global_total = self._replay_existing()

    def _replay_existing(self) -> float:
        total = 0.0
        if os.path.exists(self.usage_path):
            with open(self.usage_path) as fh:
                for line in fh:
                    try:
                        total += json.loads(line).get("cost_usd", 0.0)
                    except json.JSONDecodeError:
                        pass
        return total

    def record(self, row: dict) -> None:
        os.makedirs(os.path.dirname(self.usage_path) or ".", exist_ok=True)
        with open(self.usage_path, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        cost = row.get("cost_usd", 0.0)
        self.run_total += cost
        self.global_total += cost
        if self.run_cap is not None and self.run_total >= self.run_cap:
            raise BudgetExceeded(
                f"run budget {self.run_cap} USD reached "
                f"({self.run_total:.2f})")
        if self.global_total >= self.global_cap:
            raise BudgetExceeded(
                f"GLOBAL budget {self.global_cap} USD reached "
                f"({self.global_total:.2f})")


class LiteLLMClient:
    MAX_RETRIES = 5

    def __init__(self, model_cfg: dict):
        self.cfg = model_cfg          # {litellm_model, api_base?, price?...}

    def complete(self, prompt: str, temperature: float,
                 max_tokens: int = 4096) -> LLMReply:
        import litellm

        # per-model overrides: an explicit models.yaml max_tokens is
        # authoritative (it may RAISE the cap, e.g. thinking models need
        # room for reasoning + answer); otherwise the caller's cap applies
        max_tokens = self.cfg.get("max_tokens", max_tokens)
        extra = self.cfg.get("extra", {})
        messages = [{"role": "user", "content": prompt}]
        last_err = None
        for attempt in range(self.MAX_RETRIES):
            t0 = time.time()
            try:
                resp = litellm.completion(
                    model=self.cfg["litellm_model"],
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_base=self.cfg.get("api_base"),
                    **extra,
                )
                usage = resp.usage
                try:
                    cost = litellm.completion_cost(completion_response=resp)
                except Exception:
                    price = self.cfg.get("price_per_mtok", {})
                    cost = (usage.prompt_tokens
                            * price.get("input", 0.0)
                            + usage.completion_tokens
                            * price.get("output", 0.0)) / 1e6
                return LLMReply(
                    text=resp.choices[0].message.content or "",
                    tokens_in=usage.prompt_tokens,
                    tokens_out=usage.completion_tokens,
                    cost_usd=float(cost or 0.0),
                    latency_s=round(time.time() - t0, 2),
                )
            except Exception as e:          # rate limit / transient API error
                last_err = e
                time.sleep(min(2 ** attempt * 2, 60))
        return LLMReply("", 0, 0, 0.0, 0.0,
                        error=f"{type(last_err).__name__}: {last_err}")


class MockClient:
    """Offline stand-in for pipeline testing (never debug
    against paid API models).

    Behaviours (model name suffix):
      mock:reference  -- emits a correct oracle (per-solution phase marks,
                         derived from the SOLUTIONS the runner injects);
      mock:broken     -- same but drops one solution (fails L3);
      mock:garbage    -- non-code answer (fails extraction / L1).
    """

    def __init__(self, behaviour: str):
        self.behaviour = behaviour
        self.solutions: set[int] | None = None   # injected by the runner
        self.n_problem: int | None = None

    def complete(self, prompt: str, temperature: float,
                 max_tokens: int = 4096) -> LLMReply:
        if self.behaviour == "garbage":
            return LLMReply("I am sorry, I can only describe the algorithm "
                            "in prose.", 50, 20, 0.0, 0.0)
        sols = sorted(self.solutions or [])
        if self.behaviour == "broken" and sols:
            sols = sols[1:]
        if "## Stage 1: classical checker" in prompt:
            code = (f"SOLUTIONS = set({sols})\n\n"
                    "def check(x: int) -> bool:\n"
                    "    return x in SOLUTIONS\n")
            reply = f"```python\n{code}\n```"
        else:
            code = self._solution_marking_code(sols, self.n_problem or 1)
            reply = (f"Here is the oracle:\n```python\n{code}\n```\n"
                     "SUMMARY: rebuilt oracle from solution list")
        return LLMReply(reply, 100, 200, 0.0, 0.0)

    @staticmethod
    def _solution_marking_code(sols: list[int], n: int) -> str:
        return (
            "import math\n\n"
            f"SOLUTIONS = {sols}\n"
            f"N = {n}\n\n"
            "def build_oracle(qc, problem_qubits, ancilla_qubits):\n"
            "    for s in SOLUTIONS:\n"
            "        zeros = [problem_qubits[i] for i in range(N)"
            " if not (s >> i) & 1]\n"
            "        for q in zeros:\n"
            "            qc.x(q)\n"
            "        if N == 1:\n"
            "            qc.p(math.pi, problem_qubits[0])\n"
            "        else:\n"
            "            qc.mcp(math.pi, [problem_qubits[i] for i in "
            "range(N - 1)], problem_qubits[N - 1])\n"
            "        for q in zeros:\n"
            "            qc.x(q)\n"
        )


def make_client(model_cfg: dict):
    name = model_cfg["litellm_model"]
    if name.startswith("mock:"):
        return MockClient(name.split(":", 1)[1])
    return LiteLLMClient(model_cfg)
