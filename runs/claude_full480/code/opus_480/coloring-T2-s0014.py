from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:6]
    final_anc = ancilla_qubits[6]

    def edge_compute(uncompute=False):
        for k, (u, v) in enumerate(edges):
            a0, a1 = vq(u)
            b0, b1 = vq(v)
            e = edge_anc[k]
            # Colors: decode c=3 -> color 0. Two vertices share a color iff
            # decoded(u) == decoded(v). We compute e = 1 iff colors DIFFER (edge OK).
            #
            # Represent each vertex color by 3 indicator terms. Instead, directly
            # compute "same color" into e, then flip so e=1 means differ.
            #
            # same iff decode(a)==decode(b). Decode maps codes {0,3}->0, 1->1, 2->2.
            # Define d0 = (code==0 or code==3), d1 = (code==1), d2 = (code==2).
            # For code bits (x0 low, x1 high):
            #   code0: x1=0,x0=0 ; code3: x1=1,x0=1  -> d0 = (x0 == x1)  i.e. x0 XNOR x1
            #   code1: x1=0,x0=1 -> d1 = (x0=1,x1=0)
            #   code2: x1=0? no: code2 is x1=1,x0=0 -> d2 = (x0=0,x1=1)
            # same = d0(a)d0(b) + d1(a)d1(b) + d2(a)d2(b)
            #
            # We compute "same" into e via three multi-controlled terms.
            #
            # Term d1: controls a0=1,a1=0 and b0=1,b1=0
            # Term d2: controls a0=0,a1=1 and b0=0,b1=1
            # Term d0: a0==a1 and b0==b1. Use helper: t = a0 xor a1 (0 means d0(a) true),
            #          s = b0 xor b1. d0 both true iff t=0 and s=0.

            # d1 term
            qc.x(a1); qc.x(b1)
            qc.mcx([a0, a1, b0, b1], e)
            qc.x(a1); qc.x(b1)

            # d2 term
            qc.x(a0); qc.x(b0)
            qc.mcx([a0, a1, b0, b1], e)
            qc.x(a0); qc.x(b0)

            # d0 term: a0 xor a1 == 0 and b0 xor b1 == 0
            # fold XOR into a1 and b1, then need a1==0 and b1==0 and (a0,b0 free? no)
            # After a1 ^= a0, a1 holds a0 xor a1 = t. After b1 ^= b0, b1 = s.
            qc.cx(a0, a1); qc.cx(b0, b1)
            qc.x(a1); qc.x(b1)
            qc.mcx([a1, b1], e)
            qc.x(a1); qc.x(b1)
            qc.cx(a0, a1); qc.cx(b0, b1)

            # now e = same(u,v). flip so e = differ.
            qc.x(e)

    # compute all edge indicators
    edge_compute()

    # AND of all edge indicators -> final_anc, phase, uncompute
    qc.mcx(edge_anc, final_anc)
    qc.z(final_anc)
    qc.mcx(edge_anc, final_anc)

    # uncompute edge indicators (mirror: same operations are self-inverse per edge)
    for k, (u, v) in enumerate(reversed(edges)):
        idx = len(edges) - 1 - k
        a0, a1 = vq(u)
        b0, b1 = vq(v)
        e = edge_anc[idx]
        qc.x(e)
        qc.cx(a0, a1); qc.cx(b0, b1)
        qc.x(a1); qc.x(b1)
        qc.mcx([a1, b1], e)
        qc.x(a1); qc.x(b1)
        qc.cx(a0, a1); qc.cx(b0, b1)
        qc.x(a0); qc.x(b0)
        qc.mcx([a0, a1, b0, b1], e)
        qc.x(a0); qc.x(b0)
        qc.x(a1); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], e)
        qc.x(a1); qc.x(b1)
