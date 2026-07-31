from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells: A=(0,1), B=(2,1). Each 2 qubits: b0=low, b1=high, value v=decode(code)
    # decode: 00->0, 01->1, 10->2, 11->0
    # Grid:
    #  row0: 0  A  1     -> A must be 2 (row0 has 0,1; col1 gets A and B)
    #  row1: 2  1  0
    #  row2: 1  B  2     -> B must be 0
    # Row0 needs A=2 ; Row2 needs B=0 ; Col1 = {A,1,B} needs {0,1,2} so {A,B}={0,2}
    # => A=2, B=0. Both consistent. f=1 iff A decodes to 2 AND B decodes to 0.
    a0, a1 = problem_qubits[0], problem_qubits[1]  # cell A: b0,b1
    b0, b1 = problem_qubits[2], problem_qubits[3]  # cell B: b0,b1

    anc_A = ancilla_qubits[0]  # =1 iff A==2 (code 10: b0=0,b1=1)
    anc_B = ancilla_qubits[1]  # =1 iff B==0 (code 00 or 11)
    anc_B0 = ancilla_qubits[2]
    anc_B1 = ancilla_qubits[3]

    # A == value 2 iff code==10 exactly: b1=1, b0=0
    qc.x(a0)
    qc.ccx(a0, a1, anc_A)
    qc.x(a0)

    # B == value 0 iff code==00 or code==11 (b0==b1)
    # anc_B0 = (b0==0 and b1==0) = NOT b0 AND NOT b1
    qc.x(b0)
    qc.x(b1)
    qc.ccx(b0, b1, anc_B0)
    qc.x(b0)
    qc.x(b1)
    # anc_B1 = (b0==1 and b1==1)
    qc.ccx(b0, b1, anc_B1)
    # anc_B = anc_B0 OR anc_B1 = anc_B0 XOR anc_B1 (mutually exclusive)
    qc.cx(anc_B0, anc_B)
    qc.cx(anc_B1, anc_B)

    # phase: -1 iff anc_A AND anc_B
    qc.cz(anc_A, anc_B)

    # uncompute (mirror)
    qc.cx(anc_B1, anc_B)
    qc.cx(anc_B0, anc_B)
    qc.ccx(b0, b1, anc_B1)
    qc.x(b0)
    qc.x(b1)
    qc.ccx(b0, b1, anc_B0)
    qc.x(b0)
    qc.x(b1)
    qc.x(a0)
    qc.ccx(a0, a1, anc_A)
    qc.x(a0)
