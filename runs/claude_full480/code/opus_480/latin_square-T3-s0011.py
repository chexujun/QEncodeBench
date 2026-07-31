from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    p = problem_qubits
    anc = ancilla_qubits

    # Free cells order: 0=(1,0), 1=(1,2), 2=(2,1), 3=(2,2)
    # cell j: b0 = p[2j], b1 = p[2j+1], value: 00->0,01->1,10->2,11->0
    # grid:
    #   row0: 2 0 1
    #   row1: c0 1 c1
    #   row2: 1 c2 c3
    #
    # Constraints (all-different) that remain, treating decoded values:
    # Row1: {c0, 1, c1} distinct  -> c0 != 1, c1 != 1, c0 != c1
    # Row2: {1, c2, c3} distinct  -> c2 != 1, c3 != 1, c2 != c3
    # Col0: {2, c0, 1} distinct   -> c0 != 2, c0 != 1  (already c0!=1)
    # Col1: {0, 1, c2} distinct   -> c2 != 0, c2 != 1
    # Col2: {1, c1, c3} distinct  -> c1 != 1, c3 != 1, c1 != c3
    #
    # Since it's a Latin square, forced solution:
    # c0 in {0,2}\{2,1} = {0}; but also row1 c0!=c1. c0 must be 0.
    #   -> c0 == 0.
    # c1: row1 {0,1,c1} distinct, col2 c1!=1 -> c1 = 2. -> c1 == 2.
    # c2: col1 c2 in {2} (not 0, not1) -> c2 == 2.
    # c3: row2 {1,c2=2,c3} -> c3 = 0; col2 {1,c1=2,c3} -> c3=0 -> c3 == 0.
    #
    # So f(x)=1 iff decoded: c0=0, c1=2, c2=2, c3=0.
    # decode value of cell: code 00->0, 11->0 (value0); 10->2 (value2); 01->1; ...
    # value 0  <=> code in {00, 11} <=> (b0 == b1)
    # value 2  <=> code == 10 <=> b0=0, b1=1
    #
    # c0==0 : b0(0)=p0, b1(0)=p1 : need p0==p1
    # c1==2 : b0(1)=p2, b1(1)=p3 : need p2=0, p3=1
    # c2==2 : b0(2)=p4, b1(2)=p5 : need p4=0, p5=1
    # c3==0 : b0(3)=p6, b1(3)=p7 : need p6==p7

    # Build predicate flags into ancillas, then a single MCP for phase, then uncompute.
    # We will create per-cell "match" bits.

    # a0: c0 match (p0 == p1)  -> use ancilla, XNOR: a=1 when p0==p1
    a0, a1, a2, a3 = anc[0], anc[1], anc[2], anc[3]
    tgt = anc[4]  # collects nothing; we instead multi-control on the four flags

    # c0 == 0 : p0 == p1 : a0 = XNOR(p0,p1)
    qc.cx(p[0], a0)
    qc.cx(p[1], a0)
    qc.x(a0)  # a0 = 1 iff p0==p1

    # c3 == 0 : p6 == p7 : a3 = XNOR(p6,p7)
    qc.cx(p[6], a3)
    qc.cx(p[7], a3)
    qc.x(a3)

    # c1 == 2 : p2==0 and p3==1 : a1 = (NOT p2) AND p3
    qc.x(p[2])
    qc.ccx(p[2], p[3], a1)
    qc.x(p[2])

    # c2 == 2 : p4==0 and p5==1 : a2 = (NOT p4) AND p5
    qc.x(p[4])
    qc.ccx(p[4], p[5], a2)
    qc.x(p[4])

    # Phase -1 iff a0 & a1 & a2 & a3 all 1
    qc.h(tgt)
    qc.mcx([a0, a1, a2, a3], tgt)
    qc.h(tgt)

    # Uncompute (mirror)
    qc.x(p[4])
    qc.ccx(p[4], p[5], a2)
    qc.x(p[4])

    qc.x(p[2])
    qc.ccx(p[2], p[3], a1)
    qc.x(p[2])

    qc.x(a3)
    qc.cx(p[7], a3)
    qc.cx(p[6], a3)

    qc.x(a0)
    qc.cx(p[1], a0)
    qc.cx(p[0], a0)
