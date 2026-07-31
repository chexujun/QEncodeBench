from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells order: (0,2)=j0, (1,1)=j1, (1,2)=j2, (2,1)=j3
    # Givens grid:
    #   row0: 1 2 .        row1: 0 . .        row2: 2 . 1
    # Value qubits per free cell j: b0=problem_qubits[2j], b1=problem_qubits[2j+1]
    # Decode: 00->0, 01->1, 10->2, 11->0.  value==v tests:
    #   v0 : (not b0 and not b1) or (b0 and b1)  == (b0 == b1)  -> XNOR
    #   v1 : b0 and not b1
    #   v2 : not b0 and b1
    #
    # Constraints that must ALL hold (each cell's value in {0,1,2} auto by surjective decode):
    # Row0: cells given {1,2} + free (0,2) must be {0,1,2} => free(0,2)==0
    # Row1: given {0} + free (1,1),(1,2) => {(1,1),(1,2)} == {1,2}
    # Row2: given {2,1} + free (2,1) => free(2,1)==0
    # Col0: given {1,0,2} already complete -> ok
    # Col1: given {2} + free (1,1),(2,1) => {(1,1),(2,1)} == {0,1}
    # Col2: free (0,2),(1,2) + given {1} => {(0,2),(1,2)} == {0,2}
    #
    # Combine: (0,2)==0 and (2,1)==0.
    #  Row1: {(1,1),(1,2)}=={1,2}.  Col1: {(1,1),(2,1)}=={0,1} with (2,1)=0 => (1,1)==1.
    #  Then (1,2)==2.  Col2: {(0,2),(1,2)}=={0,2} with (0,2)=0,(1,2)==2 ok.
    # So unique solution: (0,2)=0, (1,1)=1, (1,2)=2, (2,1)=0.
    # Encode as predicate on qubits:
    #  cell0 (j=0) == 0 : b0==b1
    #  cell1 (j=1) == 1 : b0=1, b1=0
    #  cell2 (j=2) == 2 : b0=0, b1=1
    #  cell3 (j=3) == 0 : b0==b1

    b = [problem_qubits[2 * j] for j in range(4)]
    c = [problem_qubits[2 * j + 1] for j in range(4)]
    flags = ancilla_qubits[0:4]
    out = ancilla_qubits[4]

    def compute():
        # flag0: cell0 == 0  <=> b0 == c0  <=> not(b0 xor c0)
        qc.cx(b[0], flags[0]); qc.cx(c[0], flags[0]); qc.x(flags[0])
        # flag1: cell1 == 1  <=> b1==1 and c1==0
        qc.x(c[1]); qc.ccx(b[1], c[1], flags[1]); qc.x(c[1])
        # flag2: cell2 == 2  <=> b2==0 and c2==1
        qc.x(b[2]); qc.ccx(b[2], c[2], flags[2]); qc.x(b[2])
        # flag3: cell3 == 0  <=> b3 == c3
        qc.cx(b[3], flags[3]); qc.cx(c[3], flags[3]); qc.x(flags[3])

    compute()
    qc.mcx([flags[0], flags[1], flags[2], flags[3]], out)
    qc.z(out)
    qc.mcx([flags[0], flags[1], flags[2], flags[3]], out)
    # uncompute (mirror)
    qc.cx(b[3], flags[3]); qc.cx(c[3], flags[3]); qc.x(flags[3])
    qc.x(b[2]); qc.ccx(b[2], c[2], flags[2]); qc.x(b[2])
    qc.x(c[1]); qc.ccx(b[1], c[1], flags[1]); qc.x(c[1])
    qc.cx(b[0], flags[0]); qc.cx(c[0], flags[0]); qc.x(flags[0])
