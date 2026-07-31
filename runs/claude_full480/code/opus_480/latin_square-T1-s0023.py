from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Grid (rows top->bottom):
    #   1 2 0
    #   2 . 1   -> free cell 0 at (1,1)
    #   0 . 2   -> free cell 1 at (2,1)
    #
    # Free cell 0 code bits: b0=problem_qubits[0], b1=problem_qubits[1]
    # Free cell 1 code bits: b0=problem_qubits[2], b1=problem_qubits[3]
    # Decode (surjective): 00->0, 01->1, 10->2, 11->0
    #
    # Constraints to satisfy simultaneously:
    #   Row 1: {2, A, 1} all-different  -> A must be 0  (value 0)
    #   Row 2: {0, B, 2} all-different  -> B must be 1  (value 1)
    #   Col 1 (middle column): {2 (from row0), A, B} all-different
    #          given A=0, B=1 -> {2,0,1} valid.
    #
    # So the ONLY valid assignment is A=0, B=1.
    #   A == 0 : code in {00, 11}  i.e. b0==b1
    #   B == 1 : code == 01         i.e. c0(b0)=1, c1(b1)=0
    #
    # Predicate f = [A==0] AND [B==1]
    #             = (b0_A == b1_A) AND (b0_B == 1) AND (b1_B == 0)

    a0 = problem_qubits[0]  # A b0
    a1 = problem_qubits[1]  # A b1
    b0 = problem_qubits[2]  # B b0
    b1 = problem_qubits[3]  # B b1

    anc = ancilla_qubits
    eqA = anc[0]   # 1 iff a0 == a1  (A == 0)

    # Compute eqA = NOT(a0 XOR a1)
    qc.cx(a0, eqA)
    qc.cx(a1, eqA)
    qc.x(eqA)   # eqA = 1 iff a0==a1

    # B==1 condition: b0==1 and b1==0. Flip b1 so we need b1'==1.
    qc.x(b1)    # now b1 (transient) is 1 iff original b1==0

    # Phase -1 iff eqA==1 AND b0==1 AND b1'==1
    qc.h(eqA)
    qc.ccx(b0, b1, eqA)
    qc.h(eqA)

    # Uncompute
    qc.x(b1)

    qc.x(eqA)
    qc.cx(a1, eqA)
    qc.cx(a0, eqA)
