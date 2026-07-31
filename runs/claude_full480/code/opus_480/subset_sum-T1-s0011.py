from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # a = [1, 5, 5], target T = 10.
    # Subset sums: selecting elements with values summing to 10.
    # Only subset summing to 10 is {a[1], a[2]} = 5 + 5 = 10.
    # (1+5+5=11, 1+5=6, 1=1, 5=5, 0=0). So f(x)=1 iff x1=1 and x2=1 and x0=0.
    p0, p1, p2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    anc = ancilla_qubits[0]

    # compute predicate: (NOT p0) AND p1 AND p2 into anc
    qc.x(p0)
    qc.ccx(p0, p1, anc)      # anc = (NOT-original p0) AND p1
    qc.x(p0)

    # now AND with p2, phase, uncompute
    qc.h(anc)
    qc.ccx(p1, p2, anc)      # placeholder to combine; use controlled phase instead

    # Undo the misuse above and do it cleanly with a second ancilla.
    qc.ccx(p1, p2, anc)      # cancel previous ccx
    qc.h(anc)

    anc2 = ancilla_qubits[1]
    qc.x(p0)
    qc.ccx(p0, p1, anc)      # anc = (NOT p0) AND p1
    qc.x(p0)
    qc.ccx(anc, p2, anc2)    # anc2 = anc AND p2 = predicate
    qc.z(anc2)               # phase -1 iff predicate == 1
    qc.ccx(anc, p2, anc2)    # uncompute anc2
    qc.x(p0)
    qc.ccx(p0, p1, anc)      # uncompute anc
    qc.x(p0)
