from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (1, 2), (1, 3)]

    # code decode: color(c) with c in {0,1,2,3} -> {0,1,2,0}
    # color-equal predicate between two vertices u,v:
    #   colors equal iff (cu decodes == cv decodes)
    # decode: 0->0, 1->1, 2->2, 3->0
    # so "color value" k(c): k(0)=0,k(1)=1,k(2)=2,k(3)=0
    # two vertices share a color iff k(cu)==k(cv).
    #
    # For an edge, "colors differ" = NOT(k(cu)==k(cv)).
    # f(x)=1 iff for ALL edges colors differ.
    #
    # We compute per-edge a "monochromatic" flag into an edge ancilla:
    #   mono_e = 1 iff k(cu)==k(cv).
    # Then f = AND over edges of (NOT mono_e).
    # Equivalent: f = 1 iff all mono_e == 0.
    #
    # Phase -1 on states with f==1, i.e. all mono flags == 0.
    # We flip all mono flags (X) so condition becomes all==1, MCZ, then flip back.

    # helper: for vertex v, qubits (low, high)
    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # We need a scratch ancilla to build equality per edge, plus one flag per edge.
    # Available ancillas: 4. Edges: 3 -> use ancilla[0..2] as edge mono flags,
    # ancilla[3] as scratch.
    edge_flags = ancilla_qubits[0:3]
    scratch = ancilla_qubits[3]

    # color-value k(c): map codes {0,1,2,3}->{0,1,2,0}.
    # Two codes cu,cv share color iff k(cu)==k(cv).
    # Enumerate structure without baking solution set:
    # k(c)==0 for codes {00,11}; k==1 for {01}; k==2 for {10}.
    # Define indicator functions on a vertex's 2 qubits (b0 low, b1 high):
    #   isC0 = (b0==b1)         -> codes 00,11
    #   isC1 = (b0==1 & b1==0)  -> code 01
    #   isC2 = (b0==0 & b1==1)  -> code 10
    # mono(u,v) = isC0(u)&isC0(v) OR isC1(u)&isC1(v) OR isC2(u)&isC2(v).
    #
    # Compute mono into a flag via three controlled contributions.
    # Since the three color-classes are mutually exclusive per vertex,
    # the three AND-terms are mutually exclusive, so XOR-ing them equals OR.
    # We can toggle the flag for each matching class.

    def compute_edge(u, v, flag):
        u0, u1 = vq(u)
        v0, v1 = vq(v)

        # Term isC1(u)&isC1(v): b0==1,b1==0 for both.
        # control pattern: u0=1,u1=0,v0=1,v1=0 -> flip flag.
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], flag)
        qc.x(u1)
        qc.x(v1)

        # Term isC2(u)&isC2(v): b0==0,b1==1 for both.
        qc.x(u0)
        qc.x(v0)
        qc.mcx([u0, u1, v0, v1], flag)
        qc.x(u0)
        qc.x(v0)

        # Term isC0(u)&isC0(v): b0==b1 for both vertices.
        # isC0(w) = (w0==w1) = NOT(w0 XOR w1).
        # Use scratch: su = u0 XOR u1, sv handled via second scratch? Only one scratch.
        # Compute isC0 flags: we need both isC0(u) and isC0(v) true simultaneously.
        # isC0(u)&isC0(v) = NOT(u0^u1) & NOT(v0^v1).
        # Build su=u0^u1 on scratch, then we need sv too. Instead:
        # flip flag iff su==0 and sv==0.
        # Compute su into scratch, but we need a second temp. Use flag-independent trick:
        # Enumerate the two matching sub-cases explicitly (00-00 and 11-11 and 00-11 and 11-00),
        # all four combos where both vertices are in class0.
        for (a0, a1) in [(0, 0), (1, 1)]:
            for (b0, b1) in [(0, 0), (1, 1)]:
                # set controls to match pattern u0=a0,u1=a1,v0=b0,v1=b1
                flips = []
                if a0 == 0:
                    qc.x(u0); flips.append(u0)
                if a1 == 0:
                    qc.x(u1); flips.append(u1)
                if b0 == 0:
                    qc.x(v0); flips.append(v0)
                if b1 == 0:
                    qc.x(v1); flips.append(v1)
                qc.mcx([u0, u1, v0, v1], flag)
                for q in flips:
                    qc.x(q)

    # Compute all edge flags
    for e, (u, v) in enumerate(edges):
        compute_edge(u, v, edge_flags[e])

    # f = 1 iff all edge_flags == 0. Flip flags, MCZ, flip back.
    for fq in edge_flags:
        qc.x(fq)
    # MCZ over the 3 edge flags: -1 iff all == 1 (i.e. original all == 0)
    qc.h(edge_flags[2])
    qc.mcx(edge_flags[0:2], edge_flags[2])
    qc.h(edge_flags[2])
    for fq in edge_flags:
        qc.x(fq)

    # Uncompute all edge flags (mirror)
    for e, (u, v) in reversed(list(enumerate(edges))):
        compute_edge(u, v, edge_flags[e])
