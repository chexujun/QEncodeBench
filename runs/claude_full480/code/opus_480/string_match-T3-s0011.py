from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1001"
    n_text = 8
    m = len(pattern)
    offsets = list(range(n_text - m + 1))  # 0..4  -> 5 offsets

    # Fixed positions (non-wildcard) of the pattern
    fixed = [(i, int(pattern[i])) for i in range(m) if pattern[i] in "01"]

    match_ancillas = ancilla_qubits[:len(offsets)]  # one per offset (5)
    final = ancilla_qubits[len(offsets)]            # OR-accumulator ancilla (1)

    def compute_match(o, target):
        # For each fixed pattern position, we want the text bit to equal
        # the required value. Flip text qubit with X if required value is 0,
        # so that "match" means all involved qubits are |1>.
        ctrls = []
        for i, val in fixed:
            q = problem_qubits[o + i]
            if val == 0:
                qc.x(q)
            ctrls.append(q)
        qc.mcx(ctrls, target)  # target = AND of matched conditions
        # restore
        for i, val in fixed:
            if val == 0:
                qc.x(problem_qubits[o + i])

    # Compute per-offset match flags
    for idx, o in enumerate(offsets):
        compute_match(o, match_ancillas[idx])

    # OR of all match flags into `final`:
    # final = 1 iff any match flag is 1.
    # Use: final starts |0>. Apply X to each flag, MCX(all flags)->final, X back,
    # then X final  => final = NOT(all flags == 0) = OR.
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, final)
    for a in match_ancillas:
        qc.x(a)
    qc.x(final)

    # Phase kickback: -1 iff final == 1
    qc.z(final)

    # Uncompute OR
    qc.x(final)
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, final)
    for a in match_ancillas:
        qc.x(a)

    # Uncompute per-offset match flags (mirror)
    for idx, o in reversed(list(enumerate(offsets))):
        compute_match(o, match_ancillas[idx])
