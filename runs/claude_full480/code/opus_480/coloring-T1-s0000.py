from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (1, 2), (1, 3), (2, 3)]

    def vbits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:4]      # one "edge is proper (differ)" flag per edge
    out = ancilla_qubits[4]            # AND of all edge flags -> phase target

    def edge_diff(v, w, target):
        # Set target ^= 1 iff decoded_color(v) != decoded_color(w).
        # Colors equal iff codes equal OR the "both decode to color 0" case
        # ({00,11} pairing). We compute EQUAL into target, then flip so target
        # holds DIFFER = NOT EQUAL.
        a0, a1 = vbits(v)
        b0, b1 = vbits(w)

        # tmp equality bits reuse: we need scratch. Use target-building via
        # marking each "equal-color" configuration, then invert.
        #
        # Enumerate the 4 decoded colors and their code sets:
        #   color0: codes {00, 11}
        #   color1: code  {01}
        #   color2: code  {10}
        # EQUAL iff same decoded color. Mark target for each shared color.

        # color1 both: a==01 and b==01  => a0=1,a1=0,b0=1,b1=0
        qc.x(a1); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a1); qc.x(b1)

        # color2 both: a==10 and b==10  => a0=0,a1=1,b0=0,b1=1
        qc.x(a0); qc.x(b0)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a0); qc.x(b0)

        # color0 both: a in {00,11}, b in {00,11}
        # a is color0 iff a0==a1 ; b is color0 iff b0==b1.
        # Compute p = (a0==a1) into a scratch, q = (b0==b1) into scratch,
        # then target ^= p AND q. Use two fresh scratch ancillas.
        pa = a0  # placeholder markers; real scratch below
        # We need scratch qubits distinct from edge_anc/out. Reuse other
        # edge_anc slots that are guaranteed |0> at this point is unsafe, so
        # compute the four sub-cases of color0 explicitly instead:
        # a in {00,11} AND b in {00,11}  = 4 combos:
        #   (00,00),(00,11),(11,00),(11,11)
        # (00,00): all zero
        qc.x(a0); qc.x(a1); qc.x(b0); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a0); qc.x(a1); qc.x(b0); qc.x(b1)
        # (00,11): a=00,b=11
        qc.x(a0); qc.x(a1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a0); qc.x(a1)
        # (11,00): a=11,b=00
        qc.x(b0); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b0); qc.x(b1)
        # (11,11): all one
        qc.mcx([a0, a1, b0, b1], target)

        # Now target holds EQUAL. Flip to DIFFER.
        qc.x(target)

    # Compute DIFFER flag for each edge into its ancilla.
    for (v, w), t in zip(edges, edge_anc):
        edge_diff(v, w, t)

    # out = AND of all edge DIFFER flags ; phase -1 iff all edges proper.
    qc.h(out)
    qc.mcx(edge_anc, out)
    qc.h(out)

    # Uncompute edge flags (mirror).
    for (v, w), t in reversed(list(zip(edges, edge_anc))):
        edge_diff(v, w, t)
