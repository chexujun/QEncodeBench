from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells (row,col): 0:(0,0), 1:(0,1), 2:(1,2), 3:(2,2)
    # Grid givens:
    #   row0: [f0, f1, 2]
    #   row1: [2, 0, f2]
    #   row2: [1, 2, f3]
    # cols:
    #   col0: [f0, 2, 1]
    #   col1: [f1, 0, 2]
    #   col2: [2, f2, f3]
    #
    # value(cell j): code b0=pq[2j], b1=pq[2j+1]; value = 0 if code in {00,11},
    #                1 if 01, 2 if 10.
    # value==0 : (b0==b1)          -> (b0 XNOR b1)
    # value==1 : (b0==1 and b1==0)
    # value==2 : (b0==0 and b1==1)
    #
    # Constraints that involve free cells (givens already distinct where fixed):
    # Row0: f0,f1,2 distinct  -> f0!=2, f1!=2, f0!=f1
    # Row1: 2,0,f2 distinct    -> f2!=2, f2!=0
    # Row2: 1,2,f3 distinct    -> f3!=1, f3!=2
    # Col0: f0,2,1 distinct    -> f0!=2, f0!=1
    # Col1: f1,0,2 distinct    -> f1!=0, f1!=2
    # Col2: 2,f2,f3 distinct   -> f2!=2, f3!=2, f2!=f3
    #
    # Combine per cell:
    # f0: !=2 and !=1 and !=f1  => f0==0
    # f1: !=2 and !=0 and !=f0  => f1==1 (and then f0!=f1 auto)
    # f2: !=2 and !=0           => f2==1
    # f3: !=1 and !=2 and !=f2  => f3==0 and f3!=f2 (f2==1 so ok)
    #
    # So f=1 iff: f0==0, f1==1, f2==1, f3==0.
    # value==0: b0==b1 ; value==1: b0==1,b1==0.

    def q(cell, bit):
        return problem_qubits[2 * cell + bit]

    anc = ancilla_qubits

    # a0: f0 == 0  <=> b0==b1  (XNOR)
    b0, b1 = q(0, 0), q(0, 1)
    qc.cx(b0, anc[0]); qc.cx(b1, anc[0]); qc.x(anc[0])   # anc0 = XNOR

    # a1: f1 == 1 <=> b0==1 and b1==0
    b0, b1 = q(1, 0), q(1, 1)
    qc.x(b1)
    qc.ccx(b0, b1, anc[1])
    qc.x(b1)

    # a2: f2 == 1 <=> b0==1 and b1==0
    b0, b1 = q(2, 0), q(2, 1)
    qc.x(b1)
    qc.ccx(b0, b1, anc[2])
    qc.x(b1)

    # a3: f3 == 0 <=> b0==b1 (XNOR)
    b0, b1 = q(3, 0), q(3, 1)
    qc.cx(b0, anc[3]); qc.cx(b1, anc[3]); qc.x(anc[3])

    # phase -1 iff all four predicates true
    qc.h(anc[5])
    qc.mcx([anc[0], anc[1], anc[2], anc[3]], anc[5], anc[4], mode='v-chain')
    qc.h(anc[5])

    # uncompute
    b0, b1 = q(3, 0), q(3, 1)
    qc.x(anc[3]); qc.cx(b1, anc[3]); qc.cx(b0, anc[3])

    b0, b1 = q(2, 0), q(2, 1)
    qc.x(b1); qc.ccx(b0, b1, anc[2]); qc.x(b1)

    b0, b1 = q(1, 0), q(1, 1)
    qc.x(b1); qc.ccx(b0, b1, anc[1]); qc.x(b1)

    b0, b1 = q(0, 0), q(0, 1)
    qc.x(anc[0]); qc.cx(b1, anc[0]); qc.cx(b0, anc[0])
