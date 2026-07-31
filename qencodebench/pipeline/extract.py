"""Code extraction from LLM responses.

Strategies, in order:
  1. fenced ```python blocks containing `def build_oracle` (last wins);
  2. any fenced block containing `def build_oracle`;
  3. the raw text if it parses and defines build_oracle;
  4. tail-truncation repair starting at the first `def build_oracle` line,
     keeping any import lines that precede it.
Returns None when nothing extractable is found (C8 / format violation).
"""

from __future__ import annotations

import ast
import re

_FENCE_PY = re.compile(r"```(?:python|py)\s*\n(.*?)```", re.DOTALL)
_FENCE_ANY = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)


def _defines_build_oracle(code: str) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    return any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and n.name == "build_oracle" for n in tree.body)


def extract_code(text: str) -> str | None:
    if not text:
        return None
    for pattern in (_FENCE_PY, _FENCE_ANY):
        blocks = [b for b in pattern.findall(text) if "build_oracle" in b]
        if blocks:
            return blocks[-1].strip()
    if _defines_build_oracle(text):
        return text.strip()
    # tail-truncation repair
    idx = text.find("def build_oracle")
    if idx == -1:
        return None
    prefix_lines = [ln for ln in text[:idx].splitlines()
                    if ln.startswith(("import ", "from "))]
    body = text[idx:]
    lines = body.splitlines()
    for end in range(len(lines), 0, -1):
        candidate = "\n".join(prefix_lines + lines[:end])
        if _defines_build_oracle(candidate):
            return candidate.strip()
    return None
