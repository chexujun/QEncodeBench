from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Grid (rows), '.' free:
    #   row0: 1 2 0   (all given)
    #   row1: 0 . 2   free (1,1) = cell0
    #   row2: . 0 .   free (2,0) = cell1, (2,2) = cell2
    #
    # Free cell j: b0 = problem_qubits[2j], b1 = problem_qubits[2j+1], value v = (b0 + 2*b1) mod-ish
    # Decode: 00->0, 01->1, 10->2, 11->0.
    #
    # Cell0 at (1,1): row1 has given {0,2} -> must be 1. Col1 has given {2,0} -> must be 1. So cell0 == 1.
    # Cell1 at (2,0): row2 given {0}. Col0 given {1,0}. Col0 already has 0 and 1 -> cell1 must be 2.
    #                 row2 given {0} -> cell1 in {1,2}. Intersection -> cell1 == 2.
    # Cell2 at (2,2): row2 given {0}, plus cell1. Col2 given {0,2}. Col2 has 0,2 -> cell2 must be 1.
    #                 row2 then = {cell1, 0, cell2} must be {0,1,2}.
    #
    # So the UNIQUE valid completion: cell0=1, cell1=2, cell2=1.
    # But decoding is surjective, so multiple codes decode to same value:
    #   value 1 <- code 01 only
    #   value 2 <- code 10 only
    #   value 0 <- code 00 or 11
    # cell0 must be value 1 -> code 01 -> b0=1,b1=0
    # cell1 must be value 2 -> code 10 -> b0=0,b1=1
    # cell2 must be value 1 -> code 01 -> b0=1,b1=0
    #
    # Predicate f(x)=1 iff all three cells decode to the required values.
    # Required bit pattern on the 6 problem qubits:
    #   cell0: pq[0]=1, pq[1]=0
    #   cell1: pq[2]=0, pq[3]=1
    #   cell2: pq[4]=1, pq[5]=0
    #
    # This is a single marked basis state on the 6 qubits: multi-controlled Z
    # with appropriate X-conjugation on qubits that must be 0.

    pq = problem_qubits
    # want (pq0,pq1,pq2,pq3,pq4,pq5) == (1,0,0,1,1,0)
    want = [1, 0, 0, 1, 1, 0]

    # Flip qubits whose required value is 0 so that all-ones enables the control.
    zero_positions = [pq[i] for i in range(6) if want[i] == 0]
    for q in zero_positions:
        qc.x(q)

    # Multi-controlled Z on all 6 problem qubits: controls = first 5, target = last, via H-conjugated MCX.
    controls = pq[:5]
    target = pq[5]
    qc.h(target)
    qc.mcx(controls, target, ancilla_qubits[0], mode='recursion')
    qc.h(target)

    # Uncompute the X flips.
    for q in zero_positions:
        qc.x(q)
