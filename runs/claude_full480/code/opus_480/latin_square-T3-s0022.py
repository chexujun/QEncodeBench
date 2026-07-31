from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells (row,col): 0->(0,1), 1->(2,0), 2->(2,1), 3->(2,2)
    # Given grid:
    #   row0: 1 . 2
    #   row1: 2 1 0
    #   row2: . . .
    # Each free cell j: qubits (problem_qubits[2j], problem_qubits[2j+1]) = (b0,b1)
    # decode value: 00->0, 01->1, 10->2, 11->0
    # So value==0 iff (b0,b1) in {00,11}; value==1 iff (b0,b1)==(1,0)->b0=1,b1=0;
    # value==2 iff (b0,b1)==(0,1)->b0=0,b1=1.
    # value in {0,1,2,3-as-0}. Predicate: entire grid valid latin square.

    def qb(j, which):
        return problem_qubits[2 * j + which]

    # helper ancillas
    # We'll compute a set of "clause OK" flags into ancillas, AND them, phase, uncompute.
    # Instead: build a multi-controlled logic. To keep it manageable, we compute
    # for each free cell its "value indicator" using the b0,b1 bits directly in
    # constraint checks expressed as boolean equalities.

    # Denote for cell j: A_j = b0, B_j = b1.
    # v==0 : (A,B)=(0,0) or (1,1)  -> A XNOR B ... actually (0,0)&(1,1): A==B.
    # v==1 : (A,B)=(1,0)
    # v==2 : (A,B)=(0,1)
    # Note v==0 iff A==B ; v==1 iff A=1,B=0 ; v==2 iff A=0,B=1. Good, exhaustive.

    # Cell indices:
    # c0 = (0,1), c1 = (2,0), c2 = (2,1), c3 = (2,2)
    # Grid values:
    #   (0,0)=1 (0,1)=c0 (0,2)=2
    #   (1,0)=2 (1,1)=1  (1,2)=0
    #   (2,0)=c1 (2,1)=c2 (2,2)=c3

    # Constraints for a valid Latin square (rows & cols all-different, values 0,1,2):
    # Row0: {1, c0, 2} distinct -> c0 == 0.
    # Row2: {c1,c2,c3} distinct and = {0,1,2}.
    # Col0: {1,2,c1} distinct -> c1 == 0.
    # Col1: {c0,1,c2} distinct -> with c0==0, need c2==2 (and c2!=1,!=c0).
    # Col2: {2,0,c3} distinct -> c3 == 1.
    # Row2 distinct automatically satisfied if c1=0,c2=2,c3=1 -> {0,2,1} valid.
    # So the UNIQUE solution: c0=0, c1=0, c2=2, c3=1.
    # f(x)=1 iff decode(c0)=0 & decode(c1)=0 & decode(c2)=2 & decode(c3)=1.

    # Build predicate as conjunction of literal conditions on (A,B) bits.
    # c0=0 : A0==B0
    # c1=0 : A1==B1
    # c2=2 : A2=0, B2=1
    # c3=1 : A3=1, B3=0

    A0, B0 = qb(0, 0), qb(0, 1)
    A1, B1 = qb(1, 0), qb(1, 1)
    A2, B2 = qb(2, 0), qb(2, 1)
    A3, B3 = qb(3, 0), qb(3, 1)

    e0 = ancilla_qubits[0]  # c0 ok: A0==B0
    e1 = ancilla_qubits[1]  # c1 ok: A1==B1
    # c2 ok: A2==0 and B2==1
    # c3 ok: A3==1 and B3==0

    # compute e0 = NOT(A0 XOR B0)
    qc.cx(A0, e0)
    qc.cx(B0, e0)
    qc.x(e0)   # e0 = 1 iff A0==B0
    # compute e1 = NOT(A1 XOR B1)
    qc.cx(A1, e1)
    qc.cx(B1, e1)
    qc.x(e1)

    # For c2: condition A2==0 -> use X on A2 as control (control on 0).
    # For c3: condition B3==0 -> X on B3.
    # Flip so that a plain multi-control (all-ones) implements the desired pattern.
    qc.x(A2)   # now A2'=1 iff A2==0
    # B2 stays: need B2==1
    qc.x(B3)   # now B3'=1 iff B3==0
    # A3 stays: need A3==1

    # Now predicate = e0 & e1 & A2' & B2 & A3 & B3'
    controls = [e0, e1, A2, B2, A3, B3]
    # apply phase -1 when all controls are 1: multi-controlled Z.
    # Use mcp(pi, controls[:-1], controls[-1]).
    qc.mcp(math.pi, controls[:-1], controls[-1])

    # Uncompute the X flips
    qc.x(B3)
    qc.x(A2)
    # Uncompute e1
    qc.x(e1)
    qc.cx(B1, e1)
    qc.cx(A1, e1)
    # Uncompute e0
    qc.x(e0)
    qc.cx(B0, e0)
    qc.cx(A0, e0)
