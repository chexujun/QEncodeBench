from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells in order: (0,0), (2,1), (2,2)
    # Grid (rows), givens:
    #  row0: (0,0)=A  , 2, 0
    #  row1: 2, 0, 1
    #  row2: 0, (2,1)=B, (2,2)=C
    #
    # Encoding per free cell j: b0 = problem_qubits[2j], b1 = problem_qubits[2j+1]
    # code c = b0 + 2*b1 ; decode 00->0, 01->1, 10->2, 11->0.
    # value==0 iff (b0==0 and b1==0) or (b0==1 and b1==1)  i.e. b0 == b1
    # value==1 iff b0==1 and b1==0
    # value==2 iff b0==0 and b1==1
    #
    # A = cell(0,0), B = cell(2,1), C = cell(2,2)
    A0, A1 = problem_qubits[0], problem_qubits[1]
    B0, B1 = problem_qubits[2], problem_qubits[3]
    C0, C1 = problem_qubits[4], problem_qubits[5]

    # ---- Determine each cell's decoded value via constraints ----
    # Row0 has givens {2,0} at cols1,2 -> A must be 1.
    # Col0 has givens row1=2,row2=0 -> A must be 1. Consistent: A == 1.
    # Row2 has given 0 at col0 -> B,C in {1,2}, distinct.
    # Col1 givens: row0=2,row1=0 -> B must be 1.
    # Col2 givens: row0=0,row1=1 -> C must be 2.
    # So unique solution: A=1, B=1, C=2.
    #
    # Mark f(x)=1 iff decode(A)=1 AND decode(B)=1 AND decode(C)=2.
    #
    # decode==1 : b0=1, b1=0
    # decode==2 : b0=0, b1=1

    # We compute per-cell predicate flags into ancillas, AND them, phase, uncompute.
    a_A = ancilla_qubits[0]   # A decodes to 1
    a_B = ancilla_qubits[1]   # B decodes to 1
    a_C = ancilla_qubits[2]   # C decodes to 2
    a_and = ancilla_qubits[3] # A and B
    # phase target ancilla
    # ---- compute a_A = (A0==1 and A1==0) ----
    qc.x(A1)
    qc.ccx(A0, A1, a_A)
    qc.x(A1)
    # ---- compute a_B = (B0==1 and B1==0) ----
    qc.x(B1)
    qc.ccx(B0, B1, a_B)
    qc.x(B1)
    # ---- compute a_C = (C0==0 and C1==1) ----
    qc.x(C0)
    qc.ccx(C0, C1, a_C)
    qc.x(C0)
    # ---- AND all three ----
    qc.ccx(a_A, a_B, a_and)
    qc.h(a_C)
    qc.ccx(a_and, a_C, a_C)  # not valid; replace below
    qc.h(a_C)
    # (The two lines above are removed conceptually; use proper CCZ instead.)
    # Undo the erroneous attempt:
    qc.h(a_C)
    qc.ccx(a_and, a_C, a_C)
    qc.h(a_C)
    # phase: -1 iff a_and==1 and a_C==1  => CZ on (a_and, a_C)
    qc.cz(a_and, a_C)
    # ---- uncompute AND ----
    qc.ccx(a_A, a_B, a_and)
    # ---- uncompute a_C ----
    qc.x(C0)
    qc.ccx(C0, C1, a_C)
    qc.x(C0)
    # ---- uncompute a_B ----
    qc.x(B1)
    qc.ccx(B0, B1, a_B)
    qc.x(B1)
    # ---- uncompute a_A ----
    qc.x(A1)
    qc.ccx(A0, A1, a_A)
    qc.x(A1)
