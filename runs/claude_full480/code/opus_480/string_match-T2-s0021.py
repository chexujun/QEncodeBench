from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "11011?"
    n = len(problem_qubits)  # 7
    L = len(pattern)         # 6

    offsets = [0, 1]
    match_ancillas = []

    # For each offset, compute a "match" flag into an ancilla.
    for idx, o in enumerate(offsets):
        # Determine which text positions must equal which bit values.
        # For pattern position i, compare against s_(o+i).
        # Wildcard '?' imposes no constraint.
        constraints = []  # list of (qubit_index, required_value)
        for i, pc in enumerate(pattern):
            if pc == '?':
                continue
            q = problem_qubits[o + i]
            constraints.append((q, int(pc)))

        flag = ancilla_qubits[idx]
        match_ancillas.append(flag)

        # Flip control qubits so that "required value 0" becomes control-on-1.
        ctrl_qubits = []
        for q, val in constraints:
            if val == 0:
                qc.x(q)
            ctrl_qubits.append(q)

        # flag = AND of all constraints
        qc.mcx(ctrl_qubits, flag)

        # Undo the X flips on the problem qubits (flag already captured value).
        for q, val in constraints:
            if val == 0:
                qc.x(q)

    # Now match_ancillas[k] = 1 iff pattern matches at offset offsets[k].
    # f = OR of match flags. Apply phase -1 iff at least one flag is 1.
    # Use the identity: phase(-1)^(OR) via De Morgan on the two flags.
    # OR(a,b): mark unless both are 0.
    # Compute NOT a AND NOT b -> if that AND is 1, all zero (f=0).
    a0, a1 = match_ancillas[0], match_ancillas[1]

    # Flip both flags: now a AND b == 1 iff originally both were 0 (no match).
    qc.x(a0)
    qc.x(a1)
    # Apply -1 phase to states where NOT(both zero), i.e. where OR holds.
    # Equivalent: global phase then controlled correction. Use CZ-based trick:
    # Phase over OR = (global -1) * (phase +1 on the all-zero-match state).
    # Apply -1 to every state, then +1 (i.e. cancel) on the "no match" state
    # where flipped a0==1 and a1==1.
    qc.p(math.pi, a0)          # -1 on a0==1 (flipped): partial
    qc.p(math.pi, a1)          # -1 on a1==1 (flipped)
    qc.cz(a0, a1)              # +1 correction on both==1 (double -1 -> combine)
    # Net phase on flipped basis (b0,b1):
    #   (-1)^b0 * (-1)^b1 * (-1)^(b0&b1) = +1 iff (b0,b1)=(1,1), else -1.
    # (1,1) flipped == original no-match -> phase +1. Else -1 == OR. Correct.

    # Undo flag flips
    qc.x(a0)
    qc.x(a1)

    # Uncompute match flags (mirror of compute).
    for idx, o in enumerate(offsets):
        constraints = []
        for i, pc in enumerate(pattern):
            if pc == '?':
                continue
            q = problem_qubits[o + i]
            constraints.append((q, int(pc)))
        flag = ancilla_qubits[idx]
        ctrl_qubits = []
        for q, val in constraints:
            if val == 0:
                qc.x(q)
            ctrl_qubits.append(q)
        qc.mcx(ctrl_qubits, flag)
        for q, val in constraints:
            if val == 0:
                qc.x(q)
