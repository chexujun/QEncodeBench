from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells: A=(0,0), B=(0,1). Cell A -> qubits[0](b0),[1](b1); B -> [2],[3].
    # Decode surjective: 00->0, 01->1, 10->2, 11->0.
    # Grid givens:
    #  row0: A B 1     row1: 1 2 0     row2: 0 1 2
    #  col0: A 1 0     col1: B 2 1     col2: 1 0 2
    # Constraints for a valid Latin square:
    #  Row0: {A,B,1} all-different  => A!=B, A!=1, B!=1
    #  Col0: {A,1,0} all-different  => A!=1, A!=0  => A must be 2
    #  Col1: {B,2,1} all-different  => B!=2, B!=1  => B must be 0
    #  Row1,Row2,Col2 already valid (given).
    # So the UNIQUE solution: A=2 (code 10 only; 11 decodes to 0, rejected),
    # B=0 (code 00 only; 11 decodes to 0 but A already... B=0 given constraints:
    #   B in row0 must differ from A=2 and 1 -> B=0; B code 00 ->0 ok, 11->0 also value 0.
    # But wait: value 0 for B can come from code 00 OR code 11. Both decode to 0.
    #   Row0 = {A=2, B=0, 1} all different -> valid. So B=0 acceptable via 00 and 11.
    # For A: A must be 2. value 2 comes ONLY from code 10. Code 11 -> 0 (invalid).
    #   So A: b0=0,b1=1  (exactly code 10).
    # For B: value 0 from code 00 (b0=0,b1=0) or code 11 (b0=1,b1=1).
    #   i.e. B: b0 == b1 (both 0 or both 1).
    #
    # Predicate f = [A is code 10] AND [B has b0==b1].
    # A code 10: qA0==0 and qA1==1.
    # B: qB0==qB1.
    a0, a1, b0, b1 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    anc = ancilla_qubits[0]

    # Compute indicator for A==code10 into ancilla t1: need a0=0,a1=1.
    # Compute indicator for B: b0==b1 -> (b0 XOR b1)==0.
    t1 = ancilla_qubits[1]  # A indicator
    t2 = ancilla_qubits[2]  # B indicator

    # A indicator: a0==0 AND a1==1. Flip a0 so condition becomes both==1.
    qc.x(a0)
    qc.ccx(a0, a1, t1)
    qc.x(a0)

    # B indicator: b0==b1. Compute parity into t2 then invert: t2 = NOT(b0 xor b1).
    qc.cx(b0, t2)
    qc.cx(b1, t2)
    qc.x(t2)  # t2 = 1 iff b0==b1

    # Phase -1 iff t1 AND t2.
    qc.cz(t1, t2)

    # Uncompute (mirror).
    qc.x(t2)
    qc.cx(b1, t2)
    qc.cx(b0, t2)

    qc.x(a0)
    qc.ccx(a0, a1, t1)
    qc.x(a0)
