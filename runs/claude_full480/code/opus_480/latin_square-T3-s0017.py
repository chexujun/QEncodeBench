from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Grid layout (row, col), givens:
    #   (0,0)=0 (0,1)=2 (0,2)=1
    #   (1,0)=F0 (1,1)=F1 (1,2)=2
    #   (2,0)=F2 (2,1)=1  (2,2)=F3
    # Free cells: F0=(1,0), F1=(1,1), F2=(2,0), F3=(2,2)
    # Each free cell code c=b0+2*b1, decode: 00->0,01->1,10->2,11->0.
    # decoded value set is {0,1,2}; value(code)=0 if code in {00,11}, 1 if 01, 2 if 10.
    #
    # Constraints for a valid Latin square (rows/cols contain 0,1,2 once).
    # Row1: {F0,F1,2} must be a permutation -> F0,F1 in {0,1} distinct.
    # Row2: {F2,1,F3} -> F2,F3 in {0,2} distinct.
    # Col0: {0,F0,F2} -> F0,F2 in {1,2} distinct.
    # Col1: {2,F1,1} -> F1 = 0.
    # Col2: {1,2,F3} -> F3 = 0.
    #
    # Solve deductively:
    # F1=0. Row1 distinct with F0 in{0,1}, F1=0 -> F0=1.
    # F3=0. Row2 distinct F2,F3 in{0,2}, F3=0 -> F2=2.
    # Col0: F0=1,F2=2 distinct in {1,2}: OK. Col1: F1=0 OK. Col2: F3=0 OK.
    # Unique solution: F0=1 (01), F1=0 (00 or 11), F2=2 (10), F3=0 (00 or 11).
    #
    # Predicate f(x)=1 iff:
    #   F0 decodes to 1  : (b0,b1)=(1,0)
    #   F1 decodes to 0  : code in {00,11} i.e. b0==b1
    #   F2 decodes to 2  : (b0,b1)=(0,1)
    #   F3 decodes to 0  : b0==b1
    #
    # qubit indices per free cell j: b0=problem_qubits[2j], b1=problem_qubits[2j+1]
    p = problem_qubits
    F0b0, F0b1 = p[0], p[1]
    F1b0, F1b1 = p[2], p[3]
    F2b0, F2b1 = p[4], p[5]
    F3b0, F3b1 = p[6], p[7]

    a = ancilla_qubits
    # ancilla assignment: a0=F0 ok, a1=F1 ok, a2=F2 ok, a3=F3 ok, a4=partial, a5=final
    aF0, aF1, aF2, aF3, aP, aFinal = a[0], a[1], a[2], a[3], a[4], a[5]

    # --- compute per-cell predicate flags ---

    # F0 ok iff b0=1,b1=0 : set aF0 = b0 AND (NOT b1)
    qc.x(F0b1)
    qc.ccx(F0b0, F0b1, aF0)
    qc.x(F0b1)

    # F1 ok iff b0==b1 : aF1 = NOT(b0 XOR b1)
    qc.cx(F1b0, aF1)
    qc.cx(F1b1, aF1)
    qc.x(aF1)   # now aF1 = 1 iff b0==b1

    # F2 ok iff b0=0,b1=1 : aF2 = (NOT b0) AND b1
    qc.x(F2b0)
    qc.ccx(F2b0, F2b1, aF2)
    qc.x(F2b0)

    # F3 ok iff b0==b1 : aF3 = NOT(b0 XOR b3)
    qc.cx(F3b0, aF3)
    qc.cx(F3b1, aF3)
    qc.x(aF3)   # aF3 = 1 iff b0==b1

    # combine: aP = aF0 AND aF1 ; aFinal = aP AND aF2 (then AND aF3 via phase)
    qc.ccx(aF0, aF1, aP)
    qc.ccx(aP, aF2, aFinal)

    # phase: -1 iff aFinal AND aF3
    qc.cz(aFinal, aF3)

    # --- uncompute (mirror) ---
    qc.ccx(aP, aF2, aFinal)
    qc.ccx(aF0, aF1, aP)

    qc.x(aF3)
    qc.cx(F3b1, aF3)
    qc.cx(F3b0, aF3)

    qc.x(F2b0)
    qc.ccx(F2b0, F2b1, aF2)
    qc.x(F2b0)

    qc.x(aF1)
    qc.cx(F1b1, aF1)
    qc.cx(F1b0, aF1)

    qc.x(F0b1)
    qc.ccx(F0b0, F0b1, aF0)
    qc.x(F0b1)
