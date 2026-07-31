from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Grid layout (row, col) -> qubit-pair index into problem_qubits, or fixed given value.
    # Free cells order: (0,2)->fc0, (1,0)->fc1, (1,1)->fc2, (2,0)->fc3
    # Givens:
    #   (0,0)=2 (0,1)=1 (0,2)=fc0
    #   (1,0)=fc1 (1,1)=fc2 (1,2)=2
    #   (2,0)=fc3 (2,1)=2 (2,2)=1
    #
    # Value decoding of a code (b0 low, b1 high): 00->0,01->1,10->2,11->0.
    # So "value == v" predicates over (b1,b0):
    #   value==0 : (b1,b0) in {00, 11}  = (b0 == b1)
    #   value==1 : (b1,b0) == 01         = (b0=1,b1=0)
    #   value==2 : (b1,b0) == 10         = (b0=0,b1=1)
    #
    # Strategy: compute a per-cell "value indicator" ancilla is expensive.
    # Instead directly derive the full constraint as a boolean AND of "all-different"
    # conditions and phase-flip when ALL constraints satisfied.
    #
    # By Latin-square logic with the givens fixed, we enumerate which value each
    # free cell MUST take for a valid completion, then the oracle marks exactly the
    # input codes decoding to that unique assignment.
    #
    # Deduce the unique solution:
    #   Row0: 2,1,? -> (0,2) must be 0
    #   Row1: ?,?,2 with col constraints
    #   Col0: 2,?,? ; Col1: 1,?,2 -> (1,1)=? col1 has 1,?,2 -> missing 0 -> (1,1)=0
    #   Row1: ?,0,2 -> (1,0)=1
    #   Col0: 2,1,? -> (2,0)=0
    #   Check row2: 0,2,1 valid. Col2: 0,2,1 valid.
    # Unique solution: fc0=0, fc1=1, fc2=0, fc3=0.
    #
    # So f(x)=1 iff decode(fc0)=0 AND decode(fc1)=1 AND decode(fc2)=0 AND decode(fc3)=0.

    b0 = [problem_qubits[2*j] for j in range(4)]
    b1 = [problem_qubits[2*j+1] for j in range(4)]

    # Predicate literals we AND together, expressed on ancillas so all controls are |1>.
    # For value==0 (fc0,fc2,fc3): need b0 == b1. Compute p = NOT(b0 XOR b1) into ancilla.
    # For value==1 (fc1): need b0=1, b1=0. Compute p = b0 AND (NOT b1) into ancilla.

    anc = list(ancilla_qubits)

    # Ancillas 0..3 hold per-cell satisfaction bit (=1 when that cell has required value).
    # fc0 value0: a0 = (b0[0]==b1[0])
    qc.cx(b0[0], anc[0]); qc.cx(b1[0], anc[0]); qc.x(anc[0])   # anc0 = NOT(b0 xor b1)
    # fc2 value0: a1
    qc.cx(b0[2], anc[1]); qc.cx(b1[2], anc[1]); qc.x(anc[1])
    # fc3 value0: a2
    qc.cx(b0[3], anc[2]); qc.cx(b1[3], anc[2]); qc.x(anc[2])
    # fc1 value1: a3 = b0[1] AND NOT b1[1]
    qc.x(b1[1])
    qc.ccx(b0[1], b1[1], anc[3])
    qc.x(b1[1])

    # Phase flip when anc0 AND anc1 AND anc2 AND anc3 all == 1.
    qc.h(anc[4])
    qc.mcx([anc[0], anc[1], anc[2], anc[3]], anc[4])
    qc.h(anc[4])

    # Uncompute (mirror).
    qc.x(b1[1])
    qc.ccx(b0[1], b1[1], anc[3])
    qc.x(b1[1])
    qc.x(anc[2]); qc.cx(b1[3], anc[2]); qc.cx(b0[3], anc[2])
    qc.x(anc[1]); qc.cx(b1[2], anc[1]); qc.cx(b0[2], anc[1])
    qc.x(anc[0]); qc.cx(b1[0], anc[0]); qc.cx(b0[0], anc[0])
