from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Grid (rows top->bottom), '.' = free:
    #   . 2 0        free cell 0 at (0,0)
    #   0 . 2        free cell 1 at (1,1)
    #   2 0 1
    #
    # Free cell 0 code -> bits (problem_qubits[0]=b0, problem_qubits[1]=b1)
    # Free cell 1 code -> bits (problem_qubits[2]=b0, problem_qubits[3]=b1)
    # Surjective decode: 00->0, 01->1, 10->2, 11->0.
    #
    # Constraints on the two free cells:
    #  Cell0 at (0,0): row0 has {2,0}, col0 has {0,2}. So cell0 must be value 1.
    #  Cell1 at (1,1): row1 has {0,2}, col1 has {2,0}. So cell1 must be value 1.
    # And row/col all-different is then automatically satisfied (each value once).
    #
    # value(cell)=1  <=> code == 01  <=> b0==1 and b1==0.
    # (code 11 decodes to 0, code 00->0, code 10->2, only 01 gives 1.)
    #
    # f(x)=1 iff cell0 code==01 AND cell1 code==01.

    b0c0 = problem_qubits[0]  # cell0 low
    b1c0 = problem_qubits[1]  # cell0 high
    b0c1 = problem_qubits[2]  # cell1 low
    b1c1 = problem_qubits[3]  # cell1 high

    # We want phase -1 iff (b0c0=1, b1c0=0, b0c1=1, b1c1=0).
    # Flip the high bits so that all-ones controls select the target pattern.
    qc.x(b1c0)
    qc.x(b1c1)

    # 4-controlled Z on the four problem qubits (all must be 1 now).
    # Compute AND into ancillas, phase, uncompute.
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]

    qc.ccx(b0c0, b1c0, a0)   # a0 = b0c0 AND b1c0
    qc.ccx(b0c1, b1c1, a1)   # a1 = b0c1 AND b1c1
    qc.cz(a0, a1)            # phase -1 iff a0 AND a1
    qc.ccx(b0c1, b1c1, a1)   # uncompute a1
    qc.ccx(b0c0, b1c0, a0)   # uncompute a0

    # Restore high bits.
    qc.x(b1c0)
    qc.x(b1c1)
