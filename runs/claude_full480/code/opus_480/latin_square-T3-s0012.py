from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells in order: (0,1),(1,0),(1,1),(2,1). Each uses 2 qubits (b0 low, b1 high).
    # Decode: 00->0, 01->1, 10->2, 11->0.
    # Grid (givens):
    #   row0: 1  A  0     A=(0,1)
    #   row1: B  C  2     B=(1,0) C=(1,1)
    #   row2: 2  D  1     D=(2,1)
    # Constraints (all-different) after decoding:
    #   Row0: {1, A, 0} distinct  -> A must be 2  (A != 0, A != 1)
    #   Row1: {B, C, 2} distinct  -> B,C in {0,1}, B != C
    #   Row2: {2, D, 1} distinct  -> D must be 0
    #   Col0: {1, B, 2} distinct  -> B must be 0
    #   Col1: {A, C, D} distinct
    #   Col2: {0, 2, 1} ok
    # Deducing: A=2, D=0, B=0 => C=1 (row1 B!=C, C in {0,1}).
    #   Col1: {A=2, C=1, D=0} distinct -> ok automatically.
    # So the UNIQUE solution values: A=2, B=0, C=1, D=0.
    # Codes: value2 -> code10 (b0=0,b1=1); value0 -> code00 or code11; value1 -> code01.
    # A=2: (b0=0,b1=1)
    # B=0: (b0,b1) in {00,11}
    # C=1: (b0=1,b1=0)
    # D=0: (b0,b1) in {00,11}
    #
    # Qubit assignment:
    # A: b0=problem_qubits[0], b1=problem_qubits[1]
    # B: b0=problem_qubits[2], b1=problem_qubits[3]
    # C: b0=problem_qubits[4], b1=problem_qubits[5]
    # D: b0=problem_qubits[6], b1=problem_qubits[7]

    A0, A1 = problem_qubits[0], problem_qubits[1]
    B0, B1 = problem_qubits[2], problem_qubits[3]
    C0, C1 = problem_qubits[4], problem_qubits[5]
    D0, D1 = problem_qubits[6], problem_qubits[7]

    # Predicate literals we need to be true:
    #   A: A0==0 AND A1==1
    #   C: C0==1 AND C1==0
    #   B: (B0==0 AND B1==0) OR (B0==1 AND B1==1)  i.e. B0==B1
    #   D: (D0==0 AND D1==0) OR (D0==1 AND D1==1)  i.e. D0==D1
    #
    # Build helper flags into ancillas so each equals 1 exactly on the desired condition.
    # ancilla_qubits: 6 available.
    aA = ancilla_qubits[0]  # 1 iff A0==0 and A1==1
    aC = ancilla_qubits[1]  # 1 iff C0==1 and C1==0
    aB = ancilla_qubits[2]  # 1 iff B0==B1
    aD = ancilla_qubits[3]  # 1 iff D0==D1
    aE = ancilla_qubits[4]  # combine aA,aC
    aF = ancilla_qubits[5]  # combine aB,aD

    # ---- compute aA = (A0==0)&(A1==1) : NOT A0 AND A1 ----
    qc.x(A0)
    qc.ccx(A0, A1, aA)
    qc.x(A0)

    # ---- compute aC = (C0==1)&(C1==0) : C0 AND NOT C1 ----
    qc.x(C1)
    qc.ccx(C0, C1, aC)
    qc.x(C1)

    # ---- compute aB = (B0==B1) : NOT(B0 XOR B1) ----
    qc.cx(B0, aB)
    qc.cx(B1, aB)
    qc.x(aB)   # now aB = 1 iff B0==B1

    # ---- compute aD = (D0==D1) ----
    qc.cx(D0, aD)
    qc.cx(D1, aD)
    qc.x(aD)   # aD = 1 iff D0==D1

    # ---- combine ----
    qc.ccx(aA, aC, aE)   # aE = aA & aC
    qc.ccx(aB, aD, aF)   # aF = aB & aD

    # ---- phase: -1 iff aE & aF ----
    qc.cz(aE, aF)

    # ---- uncompute (mirror) ----
    qc.ccx(aB, aD, aF)
    qc.ccx(aA, aC, aE)

    qc.x(aD)
    qc.cx(D1, aD)
    qc.cx(D0, aD)

    qc.x(aB)
    qc.cx(B1, aB)
    qc.cx(B0, aB)

    qc.x(C1)
    qc.ccx(C0, C1, aC)
    qc.x(C1)

    qc.x(A0)
    qc.ccx(A0, A1, aA)
    qc.x(A0)
