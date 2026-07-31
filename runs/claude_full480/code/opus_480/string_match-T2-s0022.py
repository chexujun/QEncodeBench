from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    pattern = "?001?"
    n_text = 7
    offsets = [0, 1, 2]

    # For each offset, the fixed (non-wildcard) pattern positions impose
    # equality constraints s_(o+i) == pattern[i]. An offset "matches" iff
    # all fixed positions agree. We compute a per-offset match flag into an
    # ancilla, then combine the OR of the offset flags and phase it.

    off_ancillas = ancilla_qubits[:len(offsets)]   # one flag per offset
    or_ancilla = ancilla_qubits[len(offsets)]       # accumulates OR

    # Helper data: for each offset, list of (text_index, required_bit)
    constraints = []
    for o in offsets:
        cons = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            cons.append((o + i, int(ch)))
        constraints.append(cons)

    def flip_for_zeros(cons, undo=False):
        # X the qubits whose required bit is 0, so that after the X the
        # matching condition becomes "all controls == 1".
        for (idx, bit) in cons:
            if bit == 0:
                qc.x(problem_qubits[idx])

    # Compute each offset flag: flag = AND of (s_(o+i) == pattern[i]).
    # Strategy: X-conjugate zeros so an all-ones MCX sets the flag.
    for k, o in enumerate(offsets):
        cons = constraints[k]
        ctrls = [problem_qubits[idx] for (idx, _) in cons]
        flip_for_zeros(cons)
        qc.mcx(ctrls, off_ancillas[k])
        flip_for_zeros(cons)  # restore text qubits

    # Combine OR of the offset flags into or_ancilla using De Morgan:
    # OR = NOT(AND(NOT flag_k)). Flip all flags, MCX, flip back.
    for k in range(len(offsets)):
        qc.x(off_ancillas[k])
    qc.mcx(off_ancillas, or_ancilla)
    for k in range(len(offsets)):
        qc.x(off_ancillas[k])
    qc.x(or_ancilla)  # now or_ancilla == OR of flags

    # Phase: apply -1 iff or_ancilla == 1.
    qc.z(or_ancilla)

    # Uncompute or_ancilla (mirror of the OR computation).
    qc.x(or_ancilla)
    for k in range(len(offsets)):
        qc.x(off_ancillas[k])
    qc.mcx(off_ancillas, or_ancilla)
    for k in range(len(offsets)):
        qc.x(off_ancillas[k])

    # Uncompute each offset flag (mirror).
    for k, o in enumerate(offsets):
        cons = constraints[k]
        ctrls = [problem_qubits[idx] for (idx, _) in cons]
        flip_for_zeros(cons)
        qc.mcx(ctrls, off_ancillas[k])
        flip_for_zeros(cons)
