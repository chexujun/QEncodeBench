from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells (row,col): j0=(0,0), j1=(1,0), j2=(2,2)
    # Given grid:
    #   row0: . 2 0   -> free(0,0), givens {2,0} in row0
    #   row1: . 1 2   -> free(1,0), givens {1,2} in row1
    #   row2: 2 0 .   -> free(2,2), givens {2,0} in row2
    # col0: rows -> free(0,0), free(1,0), given 2  (row2 col0 = 2)
    # col1: givens 2,1,0 (already complete, no free)
    # col2: givens 0,2, free(2,2)
    #
    # Decoding surjective: 00->0, 01->1, 10->2, 11->0.
    # Value 0 iff code in {00,11}; value 1 iff 01; value 2 iff 10.
    #
    # Row constraints force each free cell's value:
    #   (0,0): row0 has {2,0} -> must be 1
    #   (1,0): row1 has {1,2} -> must be 0
    #   (2,2): row2 has {2,0} -> must be 1
    # Column constraints then are automatically consistent:
    #   col0: {1(free00), 0(free10), 2(given)} = {0,1,2} OK
    #   col2: {0,2 givens, 1(free22)} = {0,1,2} OK
    #
    # So f(x)=1 iff cell0==1 AND cell1==0 AND cell2==1.
    #   cell j value1 iff (b0,b1)=(1,0)
    #   cell j value0 iff (b0,b1)=(0,0) or (1,1)  == (b0==b1)
    #
    # Predicate P = A0 & A1 & A2 where:
    #   A0: cell0 == 1  -> b0=1, b1=0
    #   A1: cell1 == 0  -> b0 == b1
    #   A2: cell2 == 1  -> b0=1, b1=0

    b = problem_qubits  # b[2j]=low, b[2j+1]=high

    c0_lo, c0_hi = b[0], b[1]
    c1_lo, c1_hi = b[2], b[3]
    c2_lo, c2_hi = b[4], b[5]

    # ancillas
    a0 = ancilla_qubits[0]  # A0
    a1 = ancilla_qubits[1]  # A1 (cell1 value 0: lo==hi)
    a2 = ancilla_qubits[2]  # A2
    t1 = ancilla_qubits[3]  # temp for xnor
    m = ancilla_qubits[4]   # final predicate flag

    # ---- compute A0: c0_lo==1 and c0_hi==0 ----
    qc.x(c0_hi)
    qc.ccx(c0_lo, c0_hi, a0)
    qc.x(c0_hi)

    # ---- compute A1: c1_lo == c1_hi (XNOR) ----
    qc.cx(c1_lo, t1)
    qc.cx(c1_hi, t1)
    qc.x(t1)          # t1 = 1 iff lo==hi
    qc.cx(t1, a1)     # copy into a1
    qc.x(t1)          # restore t1 partially
    qc.cx(c1_hi, t1)
    qc.cx(c1_lo, t1)  # t1 back to 0

    # ---- compute A2: c2_lo==1 and c2_hi==0 ----
    qc.x(c2_hi)
    qc.ccx(c2_lo, c2_hi, a2)
    qc.x(c2_hi)

    # ---- combine: m = a0 & a1 & a2 ----
    qc.ccx(a0, a1, m)         # m = a0&a1  (m starts 0)
    # phase on m & a2
    qc.h(m)
    qc.ccx(a2, m, m) if False else None  # placeholder-free
    qc.h(m)
    # We instead do controlled-Z style: phase -1 iff a2 & m
    qc.cz(a2, m)
    # But cz gives phase iff a2==1 and m==1 == a0&a1&a2. Good.

    # uncompute m
    qc.ccx(a0, a1, m)

    # ---- uncompute A2 ----
    qc.x(c2_hi)
    qc.ccx(c2_lo, c2_hi, a2)
    qc.x(c2_hi)

    # ---- uncompute A1 ----
    qc.cx(c1_lo, t1)
    qc.cx(c1_hi, t1)
    qc.x(t1)
    qc.cx(t1, a1)
    qc.x(t1)
    qc.cx(c1_hi, t1)
    qc.cx(c1_lo, t1)

    # ---- uncompute A0 ----
    qc.x(c0_hi)
    qc.ccx(c0_lo, c0_hi, a0)
    qc.x(c0_hi)
