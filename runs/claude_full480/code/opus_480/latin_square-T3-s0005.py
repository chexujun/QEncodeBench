from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells (row,col): 0:(0,0), 1:(1,1), 2:(2,0), 3:(2,2)
    # Grid givens:
    #   row0: [f0, 2, 0]
    #   row1: [2, f1, 1]
    #   row2: [f2, 1, f3]
    # cell code c = b0 + 2*b1, decode 00->0,01->1,10->2,11->0 (value = c if c<3 else 0)
    #
    # We need f(x)=1 iff the completed grid is a valid Latin square.
    #
    # Constraints (each cell value in {0,1,2}):
    # Row constraints:
    #   row0: f0, 2, 0 all-different  => f0 == 1
    #   row1: 2, f1, 1 all-different  => f1 == 0
    #   row2: f2, 1, f3 all-different => {f2,f3} = {0,2}, i.e. (f2,f3) in {(0,2),(2,0)}
    # Column constraints:
    #   col0: f0, 2, f2 all-different => f0 in {0,1}, f2 in {0,1}, and f0!=f2 (excluding 2)
    #         combined with f0==1 => f2 == 0
    #   col1: 2, f1, 1 all-different => f1 == 0 (consistent)
    #   col2: 0, 1, f3 all-different => f3 == 2
    #
    # Therefore the UNIQUE solution values: f0=1, f1=0, f2=0, f3=2.
    # But codes are surjective (code 11 also -> 0). So valid codes:
    #   f0 value 1: code 01  => (b0,b1)=(1,0)
    #   f1 value 0: code 00 or 11 => (0,0) or (1,1)
    #   f2 value 0: code 00 or 11 => (0,0) or (1,1)
    #   f3 value 2: code 10 => (b0,b1)=(0,1)
    #
    # So predicate over the 8 problem qubits:
    #   q0=b0(f0)=1, q1=b1(f0)=0
    #   (q2,q3) in {(0,0),(1,1)}  i.e. q2==q3
    #   (q4,q5) in {(0,0),(1,1)}  i.e. q4==q5
    #   q6=b0(f3)=0, q7=b1(f3)=1

    q = problem_qubits
    a = ancilla_qubits

    # ancilla[0]: f0 correct = q0 AND (NOT q1)
    # ancilla[1]: f1 correct = (q2 == q3) = NOT(q2 XOR q3)
    # ancilla[2]: f2 correct = (q4 == q5) = NOT(q4 XOR q5)
    # ancilla[3]: f3 correct = (NOT q6) AND q7
    # ancilla[4]: pairwise AND accumulation
    # ancilla[5]: spare

    # Compute f0 correct into a[0]: q0 & ~q1
    qc.x(q[1])
    qc.ccx(q[0], q[1], a[0])
    qc.x(q[1])

    # Compute f1 correct into a[1]: NOT(q2 xor q3)
    qc.cx(q[2], a[1])
    qc.cx(q[3], a[1])
    qc.x(a[1])   # a[1] = NOT(q2 xor q3) = (q2==q3)

    # Compute f2 correct into a[2]: NOT(q4 xor q5)
    qc.cx(q[4], a[2])
    qc.cx(q[5], a[2])
    qc.x(a[2])   # a[2] = (q4==q5)

    # Compute f3 correct into a[3]: ~q6 & q7
    qc.x(q[6])
    qc.ccx(q[6], q[7], a[3])
    qc.x(q[6])

    # Combine: a[4] = a[0] & a[1] & a[2] & a[3]
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])

    # Phase
    qc.z(a[4])

    # Uncompute a[4]
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])

    # Uncompute a[3]
    qc.x(q[6])
    qc.ccx(q[6], q[7], a[3])
    qc.x(q[6])

    # Uncompute a[2]
    qc.x(a[2])
    qc.cx(q[5], a[2])
    qc.cx(q[4], a[2])

    # Uncompute a[1]
    qc.x(a[1])
    qc.cx(q[3], a[1])
    qc.cx(q[2], a[1])

    # Uncompute a[0]
    qc.x(q[1])
    qc.ccx(q[0], q[1], a[0])
    qc.x(q[1])
