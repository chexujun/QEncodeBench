"""Boolean IR for the neuro-symbolic compile method.

The LLM translates the natural-language problem into this JSON IR; a
deterministic, self-tested compiler turns the IR into a reversible phase
oracle.  The classical INTERPRETER below defines the IR's semantics; the
compiler is tested to agree with it exactly, so validating the IR
classically (cheap, complete) certifies the compiled circuit.

Schema (JSON):
  {"op": "and" | "or", "args": [expr, ...]}
  {"op": "not", "arg": expr}
  {"op": "bit", "i": <qubit index>, "val": 0 | 1}
      -- variable bit i equals val
  {"op": "cells_differ", "a": <cell>, "b": <cell>}
      -- 2-bit cells (cell c on qubits 2c, 2c+1), SURJECTIVE decode
         (00->0, 01->1, 10->2, 11->0): decoded values differ
  {"op": "cell_ne_const", "a": <cell>, "val": 0 | 1 | 2}
      -- decoded cell value differs from a constant
  {"op": "linsum_cmp", "terms": [[coef, bit_index], ...],
   "cmp": "==" | "!=" | "<=" | ">=", "rhs": <int>}
      -- compare sum(coef * bit) with rhs (coef >= 1 integers)
"""

from __future__ import annotations

from qencodebench.core.circuits import decode_color

IR_DOC = __doc__

_CMP = {
    "==": lambda s, r: s == r,
    "!=": lambda s, r: s != r,
    "<=": lambda s, r: s <= r,
    ">=": lambda s, r: s >= r,
}


class IRError(ValueError):
    pass


def evaluate(expr: dict, x: int) -> bool:
    """Classical semantics of the IR (the specification the compiler
    must match)."""
    op = expr.get("op")
    if op == "and":
        return all(evaluate(a, x) for a in expr["args"])
    if op == "or":
        return any(evaluate(a, x) for a in expr["args"])
    if op == "not":
        return not evaluate(expr["arg"], x)
    if op == "bit":
        return ((x >> expr["i"]) & 1) == expr["val"]
    if op == "cells_differ":
        ca = decode_color((x >> (2 * expr["a"])) & 0b11)
        cb = decode_color((x >> (2 * expr["b"])) & 0b11)
        return ca != cb
    if op == "cell_ne_const":
        return decode_color((x >> (2 * expr["a"])) & 0b11) != expr["val"]
    if op == "linsum_cmp":
        s = sum(c * ((x >> i) & 1) for c, i in expr["terms"])
        return _CMP[expr["cmp"]](s, expr["rhs"])
    raise IRError(f"unknown op {op!r}")


def _need_int(expr: dict, key: str, what: str) -> int:
    v = expr.get(key)
    if not isinstance(v, int) or isinstance(v, bool):
        raise IRError(f"{what}: field '{key}' must be an integer, "
                      f"got {v!r}")
    return v


def validate_schema(expr: dict, n_bits: int) -> None:
    """Structural validation; raises IRError (never KeyError/TypeError)
    with a helpful message -- LLM-shaped JSON must fail gracefully."""
    if not isinstance(expr, dict):
        raise IRError(f"IR node must be an object, got {type(expr).__name__}")
    op = expr.get("op")
    if op in ("and", "or"):
        args = expr.get("args")
        if not isinstance(args, list) or not args:
            raise IRError(f"'{op}' needs a non-empty args list")
        for a in args:
            validate_schema(a, n_bits)
    elif op == "not":
        if "arg" not in expr:
            raise IRError("'not' needs an 'arg'")
        validate_schema(expr["arg"], n_bits)
    elif op == "bit":
        i, val = _need_int(expr, "i", "bit"), _need_int(expr, "val", "bit")
        if not (0 <= i < n_bits) or val not in (0, 1):
            raise IRError(f"bad bit atom {expr}")
    elif op in ("cells_differ", "cell_ne_const"):
        cells = [_need_int(expr, "a", op)]
        if op == "cells_differ":
            cells.append(_need_int(expr, "b", op))
            if cells[0] == cells[1]:
                raise IRError(f"cells_differ needs two DIFFERENT cells, "
                              f"got a=b={cells[0]}")
        for c in cells:
            if not (0 <= 2 * c + 1 < n_bits):
                raise IRError(f"cell {c} out of range for {n_bits} qubits")
        if op == "cell_ne_const" and _need_int(expr, "val", op) not in \
                (0, 1, 2):
            raise IRError(f"bad cell constant {expr}")
    elif op == "linsum_cmp":
        if expr.get("cmp") not in _CMP:
            raise IRError(f"bad cmp {expr.get('cmp')!r}")
        _need_int(expr, "rhs", "linsum_cmp")
        terms = expr.get("terms")
        if not isinstance(terms, list) or not terms:
            raise IRError("linsum_cmp needs terms")
        for t in terms:
            if (not isinstance(t, list) or len(t) != 2
                    or not all(isinstance(v, int) and not isinstance(v, bool)
                               for v in t)):
                raise IRError(f"bad term {t!r}: must be [int coef, int bit]")
            c, i = t
            if c < 1 or not (0 <= i < n_bits):
                raise IRError(f"bad term {[c, i]} (coef must be >= 1, bit "
                              "in range)")
    else:
        raise IRError(f"unknown op {op!r}")
