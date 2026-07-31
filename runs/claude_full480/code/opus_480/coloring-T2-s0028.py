from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 3), (2, 4), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # Ancilla layout: one "edge-ok" flag per edge (6), plus one final flag (7th).
    edge_flags = ancilla_qubits[0:6]
    final = ancilla_qubits[6]

    def color_equal_terms(u, v, target):
        # Two vertices have equal COLOR (after surjective decode 11->00) iff:
        #   both codes are in {00,11} (color 0), or both are exactly 01, or both are exactly 10.
        # We compute an OR of these three cases into `target` using compute/uncompute.
        u0, u1 = qb(u)
        v0, v1 = qb(v)

        # We build the predicate "same color" via its three disjoint sub-cases.
        # Case A: both color 0  <=> (u0==u1) AND (v0==v1)      [since 00 and 11 both have b0==b1]
        # Case B: both == 01    <=> u0=1,u1=0,v0=1,v1=0
        # Case C: both == 10    <=> u0=0,u1=1,v0=0,v1=1
        # These three cases are mutually exclusive, so OR == XOR-sum into target.

        # --- Case A: (u0 XNOR u1) AND (v0 XNOR v1) ---
        # Compute au = NOT(u0 XOR u1) into u1? No: keep problem qubits intact; use no extra flag,
        # instead push equality onto controls via temporary X on ancilla-free scheme.
        # We use `target` as accumulator; need a scratch qubit for the AND. Reuse `final` only for
        # the top-level; here allocate a local scratch from the same pool is not available, so we
        # realize Case A with an mcx over a transformed basis using X gates on problem qubits and
        # revert them (allowed: they are uncomputed).

        # Case A: mark when b0==b1 on both. Transform so that "equal" -> all ones.
        # For a pair (b0,b1): b0==b1  <=>  b0 XOR b1 == 0. Apply cx(b0->b1): then b1 becomes b0^b1,
        # and b0==b1 iff new b1==0. So control on b0-unchanged? We need both original bits.
        # Simpler: temporarily set an indicator using the identity
        #   b0==b1  == (b0 AND b1) OR (NOT b0 AND NOT b1).
        # Implement via: X on both, mccx(...->target) for the (0,0) part; then X back; then
        # mccx for the (1,1) part.

        # Case A part 1: u=(0,0) and v=(0,0)
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        # Case A part 2: u=(1,1) and v=(1,1)
        qc.mcx([u0, u1, v0, v1], target)

        # Case B: u=(1,0) and v=(1,0)  => u0=1,u1=0,v0=1,v1=0
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u1); qc.x(v1)

        # Case C: u=(0,1) and v=(0,1)  => u0=0,u1=1,v0=0,v1=1
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u0); qc.x(v0)

    # Compute per-edge "same color" flags. flag == 1 means edge is monochromatic (BAD).
    for i, (u, v) in enumerate(edges):
        color_equal_terms(u, v, edge_flags[i])

    # f(x)=1 iff NO edge is monochromatic, i.e. all edge_flags == 0.
    # Apply phase -1 when all flags are 0: X all flags, mcp(pi), X all flags.
    for fq in edge_flags:
        qc.x(fq)
    qc.h(final)
    qc.x(final)
    qc.mcx(edge_flags, final)
    qc.x(final)
    qc.h(final)
    for fq in edge_flags:
        qc.x(fq)

    # Uncompute edge flags (mirror of compute).
    for i in reversed(range(len(edges))):
        u, v = edges[i]
        color_equal_terms(u, v, edge_flags[i])
