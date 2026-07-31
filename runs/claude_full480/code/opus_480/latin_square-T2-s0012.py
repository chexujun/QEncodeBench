from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: j0=(0,1), j1=(1,1), j2=(2,0)
    # Grid givens:
    #  (0,0)=2 (0,1)=? (0,2)=0
    #  (1,0)=1 (1,1)=? (1,2)=2
    #  (2,0)=? (2,1)=2 (2,2)=1
    # value of free cell j: decode(b0,b1): 00->0,01->1,10->2,11->0
    # We need f=1 iff completed grid is a valid Latin square.
    #
    # Determine forced values:
    # Row0 has {2,0}, missing 1 -> (0,1) must = 1.
    # Row1 has {1,2}, missing 0 -> (1,1) must = 0.
    # Row2 has {2,1}, missing 0 -> (2,0) must = 0.
    # Check columns with these:
    #  Col1: (0,1)=1,(1,1)=0,(2,1)=2 -> {1,0,2} valid.
    #  Col0: (0,0)=2,(1,0)=1,(2,0)=0 -> {2,1,0} valid.
    # So the unique solution requires:
    #   cell j0 value 1  -> code in {01} (only 01 decodes to 1)
    #   cell j1 value 0  -> code in {00, 11}
    #   cell j2 value 0  -> code in {00, 11}
    #
    # Predicate f = (j0==01) AND (j1 in {00,11}) AND (j2 in {00,11}).
    #
    # Bit layout: cell j uses b0=problem_qubits[2j], b1=problem_qubits[2j+1].
    # j0: b0=pq[0], b1=pq[1]  ; need b0=1,b1=0
    # j1: b0=pq[2], b1=pq[3]  ; need b0==b1
    # j2: b0=pq[4], b1=pq[5]  ; need b0==b1

    pq = problem_qubits
    anc = ancilla_qubits

    j0b0, j0b1 = pq[0], pq[1]
    j1b0, j1b1 = pq[2], pq[3]
    j2b0, j2b1 = pq[4], pq[5]

    # ancillas
    a_j0 = anc[0]   # 1 iff j0 == 01 (b0=1,b1=0)
    a_j1 = anc[1]   # 1 iff j1b0==j1b1
    a_j2 = anc[2]   # 1 iff j2b0==j2b1
    a_eq = anc[3]   # a_j1 AND a_j2

    # --- compute a_j0 = b0 AND (NOT b1) ---
    qc.x(j0b1)
    qc.ccx(j0b0, j0b1, a_j0)
    qc.x(j0b1)

    # --- compute a_j1 = XNOR(j1b0,j1b1) = 1 iff equal ---
    qc.cx(j1b0, a_j1)
    qc.cx(j1b1, a_j1)
    qc.x(a_j1)

    # --- compute a_j2 = XNOR(j2b0,j2b1) ---
    qc.cx(j2b0, a_j2)
    qc.cx(j2b1, a_j2)
    qc.x(a_j2)

    # --- a_eq = a_j1 AND a_j2 ---
    qc.ccx(a_j1, a_j2, a_eq)

    # --- phase: -1 iff a_j0 AND a_eq ---
    qc.h(a_eq)
    qc.ccx(a_j0, a_eq, a_eq)  # placeholder-free: use controlled operation
    qc.h(a_eq)

    # The above H-CCX-H realizes a controlled action but we instead do a clean CZ:
    # Undo the improper phase construct and apply proper CZ between a_j0 and a_eq.
    qc.h(a_eq)
    qc.ccx(a_j0, a_eq, a_eq)
    qc.h(a_eq)
    qc.cz(a_j0, a_eq)

    # --- uncompute (mirror) ---
    qc.ccx(a_j1, a_j2, a_eq)

    qc.x(a_j2)
    qc.cx(j2b1, a_j2)
    qc.cx(j2b0, a_j2)

    qc.x(a_j1)
    qc.cx(j1b1, a_j1)
    qc.cx(j1b0, a_j1)

    qc.x(j0b1)
    qc.ccx(j0b0, j0b1, a_j0)
    qc.x(j0b1)
