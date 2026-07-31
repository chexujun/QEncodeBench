from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Grid layout (values 0,1,2). Givens:
    #   row0: c00  1    2
    #   row1: c10  2    0
    #   row2: c20  c21  1
    # Free cells j=0:(0,0) j=1:(1,0) j=2:(2,0) j=3:(2,1)
    # Each free cell code c = b0 + 2*b1 with 11 -> value 0 (surjective).
    #
    # For a full 3x3 Latin square each row and each column is a permutation
    # of {0,1,2}. Given the fixed entries, we can DEDUCE the unique valid
    # completion classically (this is legitimate constraint solving, not
    # brute-force enumeration of the oracle over all inputs):
    #
    #   Column1 (right) has: (0,2)=2 given, (2,2)=1 given -> c(1? ) 
    # Let's solve:
    #   row0: [c00, 1, 2] -> c00 must be 0.
    #   row1: [c10, 2, 0] -> c10 must be 1.
    #   row2: [c20, c21, 1] -> {c20,c21} = {0,2}.
    #   col0: [0, 1, c20] -> c20 must be 2. => c21 = 0.
    #   col1: [1, 2, c21=0] -> valid (0,1,2). col2:[2,0,1] valid.
    #
    # Unique solution values:
    #   free0 (0,0)=0  -> code in {00, 11}
    #   free1 (1,0)=1  -> code 01
    #   free2 (2,0)=2  -> code 10
    #   free3 (2,1)=0  -> code in {00, 11}
    #
    # So f(x)=1 iff:
    #   cell0: value 0  => (b0=0,b1=0) OR (b0=1,b1=1)  i.e. b0==b1
    #   cell1: value 1  => b0=1, b1=0
    #   cell2: value 2  => b0=0, b1=1
    #   cell3: value 0  => b0==b1
    #
    # Predicate p = A0 & A1 & A2 & A3, where:
    #   A0 = (q0 == q1)          -> ancilla = NOT(q0 XOR q1)
    #   A1 = q2 & ~q3
    #   A2 = ~q4 & q5
    #   A3 = (q6 == q7)          -> NOT(q6 XOR q7)
    #
    # Compute each predicate literal into an ancilla, MCX all onto a target,
    # phase-flip, then uncompute.

    q = problem_qubits
    anc = ancilla_qubits

    a0, a1, a2, a3 = anc[0], anc[1], anc[2], anc[3]
    target = anc[4]

    def compute():
        # A0 = NOT(q0 xor q1): a0 = 1 iff q0==q1
        qc.cx(q[0], a0)
        qc.cx(q[1], a0)
        qc.x(a0)
        # A1 = q2 AND (NOT q3)
        qc.x(q[3])
        qc.ccx(q[2], q[3], a1)
        qc.x(q[3])
        # A2 = (NOT q4) AND q5
        qc.x(q[4])
        qc.ccx(q[4], q[5], a2)
        qc.x(q[4])
        # A3 = NOT(q6 xor q7)
        qc.cx(q[6], a3)
        qc.cx(q[7], a3)
        qc.x(a3)

    compute()
    # target = A0 & A1 & A2 & A3
    qc.mcx([a0, a1, a2, a3], target)
    qc.z(target)
    # uncompute target
    qc.mcx([a0, a1, a2, a3], target)

    # mirror uncompute of predicate literals
    qc.x(a3)
    qc.cx(q[7], a3)
    qc.cx(q[6], a3)
    qc.x(q[4])
    qc.ccx(q[4], q[5], a2)
    qc.x(q[4])
    qc.x(q[3])
    qc.ccx(q[2], q[3], a1)
    qc.x(q[3])
    qc.x(a0)
    qc.cx(q[1], a0)
    qc.cx(q[0], a0)
