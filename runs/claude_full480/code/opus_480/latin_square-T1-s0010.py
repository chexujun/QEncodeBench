import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Grid (rows top->bottom):
    #   row0: 0 1 2
    #   row1: 2 0 A      A = free cell 0 at (1,2)
    #   row2: 1 B 0      B = free cell 1 at (2,1)
    #
    # Free cell 0 (A) qubits: b0=problem_qubits[0], b1=problem_qubits[1]
    # Free cell 1 (B) qubits: b0=problem_qubits[2], b1=problem_qubits[3]
    #
    # Decoding surjective: 00->0, 01->1, 10->2, 11->0.
    #
    # Constraints for a valid Latin square:
    #   A must be the value missing from row1 {2,0} -> A = 1
    #   A must be the value missing from col2 {2,0} -> A = 1
    #   B must be the value missing from row2 {1,0} -> B = 2
    #   B must be the value missing from col1 {1,0} -> B = 2
    # So f(x)=1 iff decode(A)==1 and decode(B)==2.
    #
    # decode==1 iff code==01 iff b0=1, b1=0.
    # decode==2 iff code==10 iff b0=0, b1=1.

    a0, a1 = problem_qubits[0], problem_qubits[1]   # A
    b0, b1 = problem_qubits[2], problem_qubits[3]   # B

    anc = ancilla_qubits[0]

    # Predicate: (a0 AND NOT a1) AND (NOT b0 AND b1)
    # Flip qubits so that the all-ones condition matches:
    #   want a0=1, a1=0, b0=0, b1=1  -> flip a1 and b0.
    qc.x(a1)
    qc.x(b0)

    # Multi-controlled Z on (a0, a1, b0, b1) all == 1.
    qc.h(anc)
    qc.mcx([a0, a1, b0, b1], anc)
    qc.h(anc)

    # Uncompute the flips.
    qc.x(b0)
    qc.x(a1)
