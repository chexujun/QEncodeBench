from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    e0, e1, e2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    c1, c2 = ancilla_qubits[3], ancilla_qubits[4]
    flag = ancilla_qubits[5]

    def compute():
        # Edge covered flags: e = NOT(u OR v) computed as e set when neither endpoint in S.
        # We'll compute e_i = 1 iff edge i is UNcovered (both endpoints 0).
        # edge0=(0,2): uncovered iff x0=0 and x2=0
        qc.x(x0); qc.x(x2)
        qc.ccx(x0, x2, e0)
        qc.x(x0); qc.x(x2)
        # edge1=(1,2): uncovered iff x1=0 and x2=0
        qc.x(x1); qc.x(x2)
        qc.ccx(x1, x2, e1)
        qc.x(x1); qc.x(x2)
        # edge2=(1,3): uncovered iff x1=0 and x3=0
        qc.x(x1); qc.x(x3)
        qc.ccx(x1, x3, e2)
        qc.x(x1); qc.x(x3)

        # Count of 1-bits among x0..x3 must be <= 2.
        # Compute count into 2 count qubits (c1=LSB, c2=carry). Max relevant count for
        # detecting >2 is fine: we need to know if popcount >= 3.
        # Build popcount via ripple: use c1,c2 as a 2-bit accumulator (counts mod 4 up to 3;
        # since we only add 4 bits max count is 4, but we only care about >=3).
        # Add x0
        qc.cx(x0, c1)
        # Add x1: carry = c1 & x1, then c1 ^= x1
        qc.ccx(c1, x1, c2)
        qc.cx(x1, c1)
        # Add x2
        qc.ccx(c1, x2, c2)
        qc.cx(x2, c1)
        # Add x3
        qc.ccx(c1, x3, c2)
        qc.cx(x3, c1)
        # Now (c2,c1) holds popcount mod 4 for counts 0..3; count==4 -> c2 set twice -> back to?
        # With 4 ones: additions produce c2 toggled: track: this ripple gives c2 = (count>=2 carry).
        # To be safe about count==4, note count<=2 acceptable. count>=3 rejected.
        # popcount 3 -> (c2=1,c1=1); popcount4 -> c1=0 and c2 toggled twice=0 -> ambiguous.
        # Handle count==4 separately with a 4-controlled flag.

    compute()

    # Predicate valid = all edges covered (e0=e1=e2=0) AND count<=2.
    # count<=2 means NOT( (c2 and c1) [==3] OR count4 ).
    # Compute "bad_count" indicator into flag region using c-qubits and an extra check for 4.

    # bad if popcount==3: c2=1 and c1=1
    # bad if popcount==4: all four x =1
    # valid iff e0=e1=e2=0 AND NOT bad.

    # Use flag: set flag=1 when VALID, then Z on flag.
    # Set flag via controls all being in the "good" configuration.
    # Good config: e0=0,e1=0,e2=0, and not(c1&c2), and not(all four ones).

    # Approach: temporarily mark badness onto c2's complement is complex; instead build
    # a single multi-controlled toggle of flag with the good conditions, splitting the
    # count<=2 condition into allowed count patterns is hard. Use inclusion via extra ancilla-free logic:

    # Compute count-bad into c2 by making c2 = 1 iff popcount>=3.
    # First fix c2 for popcount==4: add correction. If all four ones, current c2=0,c1=0.
    # Toggle c2 to 1 in that case:
    qc.mcx([x0, x1, x2, x3], c2)
    # Now c2 = 1 for popcount 3 (was 1) and popcount 4 (corrected to 1); c1 irrelevant now.
    # popcount 0,1,2 -> c2 = 0. Good: c2 == bad_count indicator.

    # valid iff e0=0 and e1=0 and e2=0 and c2=0.
    qc.x(e0); qc.x(e1); qc.x(e2); qc.x(c2)
    qc.mcx([e0, e1, e2, c2], flag)
    qc.x(e0); qc.x(e1); qc.x(e2); qc.x(c2)

    qc.z(flag)

    # Uncompute flag
    qc.x(e0); qc.x(e1); qc.x(e2); qc.x(c2)
    qc.mcx([e0, e1, e2, c2], flag)
    qc.x(e0); qc.x(e1); qc.x(e2); qc.x(c2)

    # Uncompute c2 correction
    qc.mcx([x0, x1, x2, x3], c2)

    # Uncompute popcount (reverse order)
    qc.cx(x3, c1)
    qc.ccx(c1, x3, c2)
    qc.cx(x2, c1)
    qc.ccx(c1, x2, c2)
    qc.cx(x1, c1)
    qc.ccx(c1, x1, c2)
    qc.cx(x0, c1)

    # Uncompute edge flags (reverse)
    qc.x(x1); qc.x(x3)
    qc.ccx(x1, x3, e2)
    qc.x(x1); qc.x(x3)
    qc.x(x1); qc.x(x2)
    qc.ccx(x1, x2, e1)
    qc.x(x1); qc.x(x2)
    qc.x(x0); qc.x(x2)
    qc.ccx(x0, x2, e0)
    qc.x(x0); qc.x(x2)
