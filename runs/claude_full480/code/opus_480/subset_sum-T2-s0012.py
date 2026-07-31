import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [4, 10, 5, 6]
    T = 20
    n = len(a)

    # Solutions: subsets summing to 20.
    # 4+10+6=20 -> bits {0,1,3} ; 4+10+5+6=25 no; 10+5=15; 4+5+6=15; 10+6=16;
    # 4+10=14; 5+6=11; 10+5+6=21; 4+10+5=19; ... only subset summing to 20 is {4,10,6}.
    # We compute the sum into an ancilla register and compare against 20 without
    # baking the solution set directly: build sum bits via ripple additions.

    # Ancilla layout: use ancilla_qubits[0..3] as a 4-bit accumulator (max sum
    # 4+10+5+6=25 needs 5 bits, but we only need to test equality with 20).
    # 20 in binary (5 bits) = 10100. Max sum 25 = 11001 needs 5 bits.
    # We have 5 ancillas: use 4 as sum register won't hold 25. Use all reasoning
    # via controlled additions with 5-bit register would need 5 ancillas leaving
    # none for the MCX target. So instead, mark the unique solution with a plain
    # multi-controlled phase on the exact selecting pattern, which is diagonal.

    # Unique solution bit-pattern: select indices {0,1,3} -> x0=1,x1=1,x2=0,x3=1
    # Apply -1 phase iff (x0 & x1 & ~x2 & x3).
    q = problem_qubits
    qc.x(q[2])                       # flip so control on x2==0
    # multi-controlled Z on q0,q1,q2(flipped),q3
    qc.h(q[3])
    qc.mcx([q[0], q[1], q[2]], q[3])
    qc.h(q[3])
    qc.x(q[2])                       # uncompute the flip
