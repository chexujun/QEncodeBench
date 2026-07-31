"""Four-level verification orchestrator producing
verify_results.jsonl rows."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

from qiskit import QuantumCircuit, qpy

from qencodebench.core.task import TaskInstance
from qencodebench.core.transpiling import transpile_fixed
from qencodebench.verifier.functional import (
    method_a, exhaustive, FuncResult, RANDOM_EXHAUSTIVE_FRACTION,
)

SANDBOX_TIMEOUT_S = 30


class VerifierInconsistency(Exception):
    """Method A and the exhaustive check disagree: verifier bug, freeze runs."""


# ---- L1 ---------------------------------------------------------------------

# APIs that would bypass gate-level oracle construction (see prompt rules)
BANNED_ATTRS = {"unitary", "diagonal", "initialize", "prepare_state",
                "set_statevector", "hamiltonian", "squ", "isometry"}
BANNED_NAMES = {"UnitaryGate", "Operator", "Statevector", "DiagonalGate",
                "Diagonal", "Initialize", "StatePreparation", "PhaseOracle",
                "HamiltonianGate", "Isometry"}
# instruction names that betray a bypass regardless of construction path
BANNED_OP_NAMES = {"unitary", "diagonal", "initialize", "state_preparation",
                   "isometry", "hamiltonian", "phase_oracle"}


def _banned_api(tree: ast.AST) -> str | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            # methods (qc.unitary) AND module-qualified classes
            # (lib.UnitaryGate) both appear as Attribute nodes
            if node.attr in BANNED_ATTRS or node.attr in BANNED_NAMES:
                return node.attr
        if isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            return node.id
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mod = getattr(node, "module", "") or ""
            names = [a.name for a in node.names]
            if "quantum_info" in mod or any("quantum_info" in n for n in names):
                return "qiskit.quantum_info"
            if any(n in BANNED_NAMES for n in names):
                return next(n for n in names if n in BANNED_NAMES)
    return None


def check_syntax(code: str) -> tuple[bool, str | None]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    banned = _banned_api(tree)
    if banned is not None:
        return False, f"banned API: {banned}"
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and node.name == "build_oracle":
            args = node.args
            n_required = len(args.args) - len(args.defaults)
            if len(args.args) >= 3 and n_required <= 3:
                return True, None
            return False, (f"build_oracle takes {len(args.args)} args, "
                           "expected 3")
    return False, "no module-level build_oracle function"


# ---- L2 ---------------------------------------------------------------------

def sandbox_build(code: str, n_problem: int, n_total: int,
                  timeout_s: int = SANDBOX_TIMEOUT_S):
    """Run untrusted code in a subprocess; return (circuit|None, error|None).

    error is one of the fail-reason enums with detail appended."""
    with tempfile.TemporaryDirectory() as tmp:
        qpy_path = os.path.join(tmp, "circ.qpy")
        job = json.dumps({"code": code, "n_problem": n_problem,
                          "n_total": n_total, "qpy_path": qpy_path})
        runner = os.path.join(os.path.dirname(__file__),
                              "_sandbox_runner.py")
        try:
            proc = subprocess.run(
                [sys.executable, runner], input=job, capture_output=True,
                text=True, timeout=timeout_s,
            )
        except subprocess.TimeoutExpired:
            return None, "TIMEOUT"
        try:
            out = json.loads(proc.stdout.strip().splitlines()[-1])
        except (json.JSONDecodeError, IndexError):
            return None, f"RUNTIME_ERROR: sandbox crashed: {proc.stderr[-500:]}"
        if not out["ok"]:
            return None, f"RUNTIME_ERROR: {out['error']}"
        if out["width"] > n_total:
            return None, f"QUBIT_VIOLATION: width {out['width']} > {n_total}"
        with open(qpy_path, "rb") as fh:
            circ = qpy.load(fh)[0]
        return circ, None


# ---- orchestrator -----------------------------------------------------------

def _sample_hash_fraction(task_id: str, sample_key: str) -> float:
    h = hashlib.sha256(f"{task_id}|{sample_key}".encode()).digest()
    return int.from_bytes(h[:4], "big") / 2 ** 32


L4_TIMEOUT_S = 120


def _depth_isolated(circ: QuantumCircuit) -> int | None:
    """Transpile in a timeout child (wide-gate synthesis can stall)."""
    with tempfile.TemporaryDirectory() as tmp:
        qpy_path = os.path.join(tmp, "c.qpy")
        with open(qpy_path, "wb") as fh:
            qpy.dump(circ, fh)
        runner = os.path.join(os.path.dirname(__file__),
                              "_transpile_runner.py")
        try:
            proc = subprocess.run(
                [sys.executable, runner],
                input=json.dumps({"qpy_path": qpy_path}),
                capture_output=True, text=True, timeout=L4_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return None
        for line in proc.stdout.splitlines():
            if line.startswith("QEB_L4:"):
                return json.loads(line[len("QEB_L4:"):])["depth"]
        return None


def _resource_check(circ: QuantumCircuit, inst: TaskInstance):
    """Returns (status, n_used, depth): status in ok|depth_exceeded|timeout."""
    touched = {q for ci in circ.data for q in ci.qubits}
    n_used = len({circ.find_bit(q).index for q in touched})
    if _simulation_risk(circ):
        depth = _depth_isolated(circ)
        if depth is None:
            return "timeout", n_used, None
    else:
        depth = transpile_fixed(circ).depth()
    return ("ok" if depth <= inst.max_depth else "depth_exceeded",
            n_used, depth)


def verify_circuit(circ: QuantumCircuit, n_problem: int, task_id: str,
                   solutions: set[int],
                   sample_key: str = "0",
                   force_exhaustive: bool = False) -> FuncResult:
    """L3 only, in-process, on an already-built circuit (also used for
    reference oracles and mutants in the self-check suite)."""
    from qencodebench.verifier.functional import MAX_DIAG_CIRCUIT_SIZE

    res = method_a(circ, n_problem, solutions)
    do_spot = (_sample_hash_fraction(task_id, sample_key)
               < RANDOM_EXHAUSTIVE_FRACTION)
    spot_affordable = (circ.size() <= MAX_DIAG_CIRCUIT_SIZE
                       and (1 << n_problem) * max(circ.size(), 1) <= 5e8)
    if res.passed and res.method == "A" and (do_spot or force_exhaustive) \
            and spot_affordable:
        ex = exhaustive(circ, n_problem, solutions)
        if ex.passed != res.passed:
            raise VerifierInconsistency(
                f"{task_id}: method A pass but exhaustive fail")
        res.method = "A+exhaustive"
    return res


# ---- simulation-risk isolation ---------------------------------------------

L3_TIMEOUT_S = 180
MAX_INPROCESS_GATES = 30_000
MAX_INSTRUCTION_WIDTH = 6      # empirically, Aer/transpile pathologies all
                               # involved wide multi-controlled gates (a
                               # 12-wide mcx + resets hung Aer for hours);
                               # anything wider verifies in the timeout child

# non-unitary instructions violate the oracle contract ("no measurement,
# no reset") AND can fake ancilla cleanliness on basis states
FORBIDDEN_OPS = {"reset", "measure", "measure_all", "initialize"}


def forbidden_instruction(circ: QuantumCircuit, _depth: int = 0) -> str | None:
    """Nested reset/measure inside CUSTOM instructions and bypass-op names
    (unitary/diagonal/...) are contract violations too.  Only generic
    Instruction/Gate wrappers are recursed (standard-library gates have
    deep benign definitions and cannot hide a reset)."""
    from qiskit.circuit import Instruction, Gate

    if _depth > 4:
        return None
    for ci in circ.data:
        op = ci.operation
        name = op.name
        if name in FORBIDDEN_OPS:
            return name
        if any(b in name.lower() for b in BANNED_OP_NAMES):
            return name
        if type(op) in (Instruction, Gate):        # custom wrappers only
            defn = getattr(op, "definition", None)
            if defn is not None:
                bad = forbidden_instruction(defn, _depth + 1)
                if bad is not None:
                    return bad
    return None


def _simulation_risk(circ: QuantumCircuit) -> bool:
    if circ.size() > MAX_INPROCESS_GATES:
        return True
    if forbidden_instruction(circ) is not None:
        return True                      # defensive; L2 rejects these anyway
    return any(len(ci.qubits) > MAX_INSTRUCTION_WIDTH for ci in circ.data)


def verify_functional(circ: QuantumCircuit, inst: TaskInstance,
                      solutions: set[int],
                      sample_key: str = "0") -> FuncResult:
    """L3 with wall-clock protection: risky circuits run in a child
    process under L3_TIMEOUT_S; normal circuits stay in-process."""
    if not _simulation_risk(circ):
        return verify_circuit(circ, inst.n_problem_qubits, inst.task_id,
                              solutions, sample_key=sample_key)
    with tempfile.TemporaryDirectory() as tmp:
        qpy_path = os.path.join(tmp, "cand.qpy")
        with open(qpy_path, "wb") as fh:
            qpy.dump(circ, fh)
        job = json.dumps({
            "qpy_path": qpy_path, "n_problem": inst.n_problem_qubits,
            "task_id": inst.task_id, "solutions": sorted(solutions),
            "sample_key": sample_key,
        })
        runner = os.path.join(os.path.dirname(__file__), "_l3_runner.py")
        try:
            proc = subprocess.run([sys.executable, runner], input=job,
                                  capture_output=True, text=True,
                                  timeout=L3_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return FuncResult(
                False, "TIMEOUT", None, [], "A-isolated",
            )
        for line in proc.stdout.splitlines():
            if line.startswith("QEB_L3_FREEZE:"):
                raise VerifierInconsistency(line[len("QEB_L3_FREEZE:"):])
            if line.startswith("QEB_L3:"):
                d = json.loads(line[len("QEB_L3:"):])
                return FuncResult(**d)
        return FuncResult(False,
                          f"RUNTIME_ERROR: l3 worker crashed: "
                          f"{proc.stderr[-300:]}", None, [], "A-isolated")


def verify_sample(code: str | None, inst: TaskInstance, solutions: set[int],
                  model: str = "", method: str = "direct",
                  sample_idx: int = 0) -> dict:
    """Full L1-L4 pipeline for one model output; returns a
    verify_results.jsonl row."""
    from qencodebench.verifier import VERIFIER_VERSION

    t0 = time.time()
    row = {
        "task_id": inst.task_id, "model": model, "method": method,
        "sample_idx": sample_idx,
        "level_reached": None,
        "pass": {"L1": None, "L2": None, "L3": None, "L4": None},
        "fail_reason": None,
        "mark_accuracy": None,
        "counterexamples": [],
        "n_qubits_used": None, "depth_transpiled": None,
        "ref_qubits": inst.ref_qubits, "ref_depth": inst.ref_depth,
        "verify_time_s": None,
        "verifier_version": VERIFIER_VERSION,
    }

    def done(level: str):
        row["level_reached"] = level
        row["verify_time_s"] = round(time.time() - t0, 3)
        return row

    # L1
    row["level_reached"] = "L1_SYNTAX"
    if code is None:
        row["pass"]["L1"] = False
        row["fail_reason"] = "SYNTAX_ERROR: no code extracted"
        return done("L1_SYNTAX")
    ok, err = check_syntax(code)
    row["pass"]["L1"] = ok
    if not ok:
        row["fail_reason"] = f"SYNTAX_ERROR: {err}"
        return done("L1_SYNTAX")

    # L2
    circ, err = sandbox_build(code, inst.n_problem_qubits,
                              inst.max_total_qubits)
    if circ is not None:
        bad_op = forbidden_instruction(circ)
        if bad_op is not None:
            circ, err = None, (f"RUNTIME_ERROR: forbidden non-unitary "
                               f"instruction '{bad_op}' (contract: no "
                               f"measurement/reset)")
    row["pass"]["L2"] = circ is not None
    if circ is None:
        row["fail_reason"] = err
        return done("L2_EXEC")

    # L3
    sample_key = f"{model}|{method}|{sample_idx}"
    func = verify_functional(circ, inst, solutions, sample_key=sample_key)
    row["pass"]["L3"] = func.passed
    row["mark_accuracy"] = func.mark_accuracy
    row["counterexamples"] = func.counterexamples
    if not func.passed:
        row["fail_reason"] = func.fail_reason
        if func.fail_reason == "MARK_MISMATCH" and func.marked is not None:
            try:
                from qencodebench.verifier.diagnosis import diagnose
                row["behavior_diff"] = diagnose(set(func.marked), inst,
                                                solutions).text
            except Exception:               # diagnosis is best-effort
                pass
        return done("L3_FUNC")

    # L4
    status, n_used, depth = _resource_check(circ, inst)
    row["n_qubits_used"] = n_used
    row["depth_transpiled"] = depth
    row["pass"]["L4"] = status == "ok"
    if status == "depth_exceeded":
        row["fail_reason"] = "DEPTH_EXCEEDED"
    elif status == "timeout":
        row["fail_reason"] = "TIMEOUT"
    return done("L4_RES")
