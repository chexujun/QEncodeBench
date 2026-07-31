from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "001??0"
    n = 7
    L = len(pattern)
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c in "01"]

    def compute_match(offset, target):
        # Flip target to |1> iff text matches pattern at this offset.
        flips = []
        for i, bit in fixed:
            q = problem_qubits[offset + i]
            if bit == 0:
                qc.x(q)
                flips.append(q)
            else:
                flips.append(q)
        controls = [problem_qubits[offset + i] for i, _ in fixed]
        qc.mcx(controls, target)
        for q in flips:
            qc.x(q)  # undo the X we applied for bit==0 controls; for bit==1 this is wrong

    # We need clean compute/uncompute. Redo carefully.

    a0 = ancilla_qubits[0]  # match at offset 0
    a1 = ancilla_qubits[1]  # match at offset 1
    a2 = ancilla_qubits[2]  # OR result

    def match_compute(offset, target):
        xed = []
        for i, bit in fixed:
            q = problem_qubits[offset + i]
            if bit == 0:
                qc.x(q)
                xed.append(q)
        controls = [problem_qubits[offset + i] for i, _ in fixed]
        qc.mcx(controls, target)
        for q in xed:
            qc.x(q)

    # Compute a0 = match at offset 0, a1 = match at offset 1
    match_compute(0, a0)
    match_compute(1, a1)

    # a2 = a0 OR a1 = NOT( (NOT a0) AND (NOT a1) )
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.ccx(a0, a1, a2)
    qc.x(a0)
    qc.x(a1)

    # phase on a2
    qc.z(a2)

    # uncompute a2
    qc.x(a0)
    qc.x(a1)
    qc.ccx(a0, a1, a2)
    qc.x(a2)
    qc.x(a0)
    qc.x(a1)

    # uncompute a1, a0
    match_compute(1, a1)
    match_compute(0, a0)
