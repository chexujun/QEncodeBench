from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Grid layout (row, col), givens:
    #   2 0 .
    #   . 1 2
    #   . 2 .
    # Free cells in order: (0,2), (1,0), (2,0), (2,2)
    # Free cell j uses low bit problem_qubits[2j], high bit problem_qubits[2j+1].
    # Decode: 00->0, 01->1, 10->2, 11->0 (surjective).
    #
    # Value equality among free cells / givens is what we constrain.
    # Encode "cell holds value v" as predicates on its two code bits (b0 low, b1 high):
    #   val0 : (code==00) or (code==11)  ->  b0 == b1        -> XNOR(b0,b1)
    #   val1 : (code==01)                ->  b0 & ~b1
    #   val2 : (code==10)                ->  ~b0 & b1
    #
    # Free cells: F0=(0,2), F1=(1,0), F2=(2,0), F3=(2,2)
    # Rows:
    #   Row0: givens {2,0}, free F0 -> F0 must be 1
    #   Row1: givens {1,2}, free F1 -> F1 must be 0
    #   Row2: given  {2},   free F2,F3 -> {F2,F3} must be {0,1} in some order
    # Cols:
    #   Col0: givens {2(r0)}, free F1(r1),F2(r2) -> {F1,F2} must be {0,1}
    #   Col1: givens {0,1,2} full -> ok
    #   Col2: givens {2(r1)}, free F0(r0),F3(r2) -> {F0,F3} must be {0,1}
    #
    # Combine: F0=1, F1=0. Then:
    #   Row2: {F2,F3}={0,1}
    #   Col0: {F1=0,F2} => F2 must be 1
    #   Col2: {F0=1,F3} => F3 must be 0
    #   Row2 with F2=1,F3=0 -> {1,0} OK.
    # So unique solution: F0=1, F1=0, F2=1, F3=0.
    #
    # Predicate f(x)=1 iff  val1(F0) & val0(F1) & val1(F2) & val0(F3).

    def bits(j):
        return problem_qubits[2 * j], problem_qubits[2 * j + 1]

    # Ancillas hold per-cell predicate results, then combine with a multi-controlled Z.
    a = ancilla_qubits

    b0_0, b1_0 = bits(0)  # F0 must be val1: b0 & ~b1
    b0_1, b1_1 = bits(1)  # F1 must be val0: b0 == b1
    b0_2, b1_2 = bits(2)  # F2 must be val1: b0 & ~b1
    b0_3, b1_3 = bits(3)  # F3 must be val0: b0 == b1

    # --- compute F0 val1 into a[0]: a0 = b0_0 & ~b1_0 ---
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a[0])
    qc.x(b1_0)

    # --- compute F1 val0 into a[1]: a1 = XNOR(b0_1,b1_1) ---
    qc.cx(b0_1, a[1])
    qc.cx(b1_1, a[1])
    qc.x(a[1])  # a1 = ~(b0_1 xor b1_1)

    # --- compute F2 val1 into a[2]: a2 = b0_2 & ~b1_2 ---
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, a[2])
    qc.x(b1_2)

    # --- compute F3 val0 into a[3]: a3 = XNOR(b0_3,b1_3) ---
    qc.cx(b0_3, a[3])
    qc.cx(b1_3, a[3])
    qc.x(a[3])

    # --- phase: -1 iff a0 & a1 & a2 & a3 ---
    qc.h(a[3])
    qc.mcx([a[0], a[1], a[2]], a[3])
    qc.h(a[3])

    # --- uncompute (mirror) ---
    qc.x(a[3])
    qc.cx(b1_3, a[3])
    qc.cx(b0_3, a[3])

    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, a[2])
    qc.x(b1_2)

    qc.x(a[1])
    qc.cx(b1_1, a[1])
    qc.cx(b0_1, a[1])

    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a[0])
    qc.x(b1_0)
