from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (2, 4), (3, 4)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # Ancilla layout: one "edge-ok" flag per edge, plus one final flag.
    # We have 5 ancillas for 4 edges + 1 final = 5. Good.
    edge_flags = ancilla_qubits[:len(edges)]        # 4 flags
    final = ancilla_qubits[len(edges)]              # 1 final flag

    def color_equal_compute(u, v, flag):
        # Set `flag = 1` iff decoded_color(u) == decoded_color(v).
        # Codes: 00->0, 01->1, 10->2, 11->0.  So colors equal iff:
        #   (both decode to 0): u in {00,11} and v in {00,11}, OR
        #   u == v in {01, 10}.
        # Decoded color as a function of (b0,b1):
        #   color0 <=> (b0==b1)  [00 or 11]
        #   color1 <=> (b0=1,b1=0)
        #   color2 <=> (b0=0,b1=1)
        # Equal colors <=> both color0, or both color1, or both color2.
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        # We'll compute three sub-terms into scratch using the flag qubit
        # via toffoli accumulation. Need scratch qubits; reuse pattern with
        # multi-controlled X into flag for each matching pattern, but patterns
        # overlap in basis states? They are mutually exclusive basis-state sets
        # for the pair, so we can OR by simply XOR-ing (disjoint) into flag.

        # both color0: (u0==u1) AND (v0==v1).
        # Express u0==u1 by temporarily making a control condition. We build it
        # with an ancilla-free trick: (u0==u1) = NOT(u0 XOR u1).
        # We need AND of two equalities plus the color1/color2 exact matches.
        # Use the `final`-adjacent free scratch? We only have flag here.
        # Instead enumerate the 3 disjoint accepting joint-patterns via mcx.

        # both color1: u=10 (u0=1,u1=0) and v=10 (v0=1,v1=0)
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], flag)
        qc.x(u1); qc.x(v1)

        # both color2: u=01 (u0=0,u1=1) and v=01
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], flag)
        qc.x(u0); qc.x(v0)

        # both color0: u in {00,11}, v in {00,11}.
        # u in {00,11} <=> u0==u1 ; v in {00,11} <=> v0==v1.
        # Enumerate the 4 disjoint (u,v) combos: (00,00),(00,11),(11,00),(11,11)
        for uc in [(0, 0), (1, 1)]:
            for vc in [(0, 0), (1, 1)]:
                flips = []
                if uc[0] == 0: flips.append(u0)
                if uc[1] == 0: flips.append(u1)
                if vc[0] == 0: flips.append(v0)
                if vc[1] == 0: flips.append(v1)
                for q in flips: qc.x(q)
                qc.mcx([u0, u1, v0, v1], flag)
                for q in flips: qc.x(q)

    # Compute per-edge "equal-color" flags (flag=1 means BAD edge).
    for (u, v), fl in zip(edges, edge_flags):
        color_equal_compute(u, v, fl)

    # f(x)=1 iff ALL edges are good, i.e. every edge_flag == 0.
    # Compute `final = 1` iff all edge_flags are 0.
    for fl in edge_flags:
        qc.x(fl)
    qc.mcx(edge_flags, final)
    for fl in edge_flags:
        qc.x(fl)

    # Apply phase -1 when final == 1.
    qc.z(final)

    # Uncompute final.
    for fl in edge_flags:
        qc.x(fl)
    qc.mcx(edge_flags, final)
    for fl in edge_flags:
        qc.x(fl)

    # Uncompute edge flags (mirror).
    for (u, v), fl in zip(edges, edge_flags):
        color_equal_compute(u, v, fl)
