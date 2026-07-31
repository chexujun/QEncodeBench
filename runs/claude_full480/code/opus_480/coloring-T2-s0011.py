from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    edges = [(0, 1), (0, 4), (1, 2), (2, 3), (3, 4)]

    def vqubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # 5 edge-ancillas hold "edge is monochromatic (same color)" flags,
    # 1 final ancilla accumulates "all edges properly colored" for the phase.
    edge_anc = ancilla_qubits[:5]
    final = ancilla_qubits[5]

    def edge_same_compute(u, v, anc):
        # Colors: c in {0,1,2,3} with 3 decoding to 0. Two vertices share a
        # color iff codes equal, OR one code is 00 and the other is 11
        # (both color 0), OR both codes are in {00,11}.
        # Equivalent: same color iff (a0,a1) and (b0,b1) decode equal.
        # Decode: color0 = {00,11}, color1={01}, color2={10}.
        # same color iff:
        #   both in {00,11}  -> color0
        #   both == 01
        #   both == 10
        a0, a1 = vqubits(u)
        b0, b1 = vqubits(v)
        # Compute predicate "same color" into anc via sum of the 3 disjoint
        # AND terms (they are mutually exclusive, so XOR == OR here).

        # term color1: a==01 and b==01  => a0=1,a1=0,b0=1,b1=0
        qc.x(a1); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], anc)
        qc.x(a1); qc.x(b1)

        # term color2: a==10 and b==10  => a0=0,a1=1,b0=0,b1=1
        qc.x(a0); qc.x(b0)
        qc.mcx([a0, a1, b0, b1], anc)
        qc.x(a0); qc.x(b0)

        # term color0: a in {00,11} and b in {00,11}
        # a in {00,11} means a0==a1 ; b in {00,11} means b0==b1.
        # Flag pa = (a0==a1) = NOT(a0 xor a1), pb similarly, then anc ^= pa & pb.
        # Compute a0 xor a1 into a0 (temporarily), b0 xor b1 into b0.
        qc.cx(a1, a0)   # a0 = a0 xor a1  -> 0 iff a in {00,11}
        qc.cx(b1, b0)   # b0 = b0 xor b1  -> 0 iff b in {00,11}
        qc.x(a0); qc.x(b0)   # now a0=1 iff a in{00,11}, b0=1 iff b in{00,11}
        qc.ccx(a0, b0, anc)
        qc.x(a0); qc.x(b0)
        qc.cx(b1, b0)   # uncompute
        qc.cx(a1, a0)

    # Compute all edge "same color" flags.
    for (u, v), anc in zip(edges, edge_anc):
        edge_same_compute(u, v, anc)

    # f(x)=1 iff NO edge is monochromatic, i.e. all edge_anc == 0.
    # final = AND(all edge_anc == 0): flip edge_anc bits, mcx, flip back.
    for anc in edge_anc:
        qc.x(anc)
    qc.mcx(edge_anc, final)
    for anc in edge_anc:
        qc.x(anc)

    # Phase.
    qc.z(final)

    # Uncompute final.
    for anc in edge_anc:
        qc.x(anc)
    qc.mcx(edge_anc, final)
    for anc in edge_anc:
        qc.x(anc)

    # Uncompute edge flags (mirror).
    for (u, v), anc in reversed(list(zip(edges, edge_anc))):
        edge_same_compute(u, v, anc)
