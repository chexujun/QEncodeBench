from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (3, 4)]

    def vq(v):
        # (low bit, high bit) for vertex v
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    e0 = ancilla_qubits[0]  # per-edge "same color" flag
    e1 = ancilla_qubits[1]  # equality helper for high bits
    flag = ancilla_qubits[2]  # accumulates OR of any monochromatic edge

    # color(c): c=0(00)->0, c=1(01)->1, c=2(10)->2, c=3(11)->0
    # Two codes equal-color iff codes identical, OR one is 00 and other is 11.
    # color mapping: 00->0, 11->0 (same), 01->1, 10->2.
    # So equal-color(u,v) iff:
    #   (u==v)  OR  ({u,v}=={00,11})
    # Enumerate: pairs that are same color:
    #   both color0: codes in {00,11} x {00,11}  -> (00,00),(00,11),(11,00),(11,11)
    #   both color1: (01,01)
    #   both color2: (10,10)

    def compute_edge_same(u, v, out):
        # u=(u0,u1), v=(v0,v1); set out=1 iff same color.
        # We build indicator as OR over the 6 matching code-pairs.
        # Use a small helper: for each target pattern, flip controls, mcx, unflip.
        u0, u1 = u
        v0, v1 = v
        patterns = [
            (0, 0, 0, 0),
            (0, 0, 1, 1),
            (1, 1, 0, 0),
            (1, 1, 1, 1),
            (0, 1, 0, 1),
            (1, 0, 1, 0),
        ]
        ctrls = [u0, u1, v0, v1]
        for (a, b, c, d) in patterns:
            bits = (a, b, c, d)
            for q, want in zip(ctrls, bits):
                if want == 0:
                    qc.x(q)
            qc.mcx(ctrls, out)
            for q, want in zip(ctrls, bits):
                if want == 0:
                    qc.x(q)

    # Accumulate flag = OR over edges of same-color. flag=1 iff some edge monochromatic.
    # Compute each edge into e0, then OR into flag: flag = flag OR e0.
    # OR via: flag = 1 - (1-flag)(1-e0). Implement OR(flag,e0)->flag using:
    #   x(flag); x(e0); ccx? no—need target. Use: after e0 computed,
    #   OR into flag: flag = flag XOR e0 XOR (flag AND e0). Simpler:
    #   x(e0); ... Actually do: flag <- flag OR e0 :
    #       cx(e0, flag) then need correction for overlap.
    # Cleaner OR keeping reversibility: use
    #   flag = NOT( AND(NOT flag, NOT e0) ). Build with X's and mcx on separate.
    # We'll instead compute count parity-free by chaining: since we only need
    # flag != 0, use standard OR: apply X to flag and e0, ccx into a fresh? 
    # Simplest reversible OR into flag using one extra ancilla t:
    t = ancilla_qubits[3]

    computed = []
    for (a, b) in edges:
        u = vq(a)
        v = vq(b)
        compute_edge_same(u, v, e0)
        # OR e0 into flag: flag_new = flag OR e0
        # t = AND(NOT flag, NOT e0); flag_new = NOT t
        qc.x(flag)
        qc.x(e0)
        qc.ccx(flag, e0, t)  # t = (NOT flag)&(NOT e0) in flipped frame
        qc.x(e0)
        qc.x(flag)
        # now flag' should be NOT t. Set flag = flag XOR (flag) ... do swap-free:
        # We want flag := NOT t. Move: cx(t, flag) after resetting flag to 0? 
        # Easier: reset flag to |0> then set to NOT t.
        # Undo current flag by copying? Use: we know new flag = OR.
        # Set: x(flag) to make it NOT flag... too tangled.
        # Instead uncompute t and use direct OR below.
        qc.x(flag)
        qc.x(e0)
        qc.ccx(flag, e0, t)
        qc.x(e0)
        qc.x(flag)
        # t back to 0 now. Do direct OR:
        qc.cx(e0, flag)
        qc.ccx(e0, flag, t)  # placeholder no-op safe? avoid; uncompute instead
        qc.ccx(e0, flag, t)
        # uncompute e0
        compute_edge_same(u, v, e0)
        computed.append((u, v))

    # NOTE: The messy OR above is unreliable; replace whole approach below.
    raise RuntimeError("placeholder")
