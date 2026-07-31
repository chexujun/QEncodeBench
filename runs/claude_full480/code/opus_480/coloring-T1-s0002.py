from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (2, 3), (3, 4)]

    def eq_marker(u, v, target):
        # After this compute block, `target` is flipped iff vertices u and v
        # decode to the SAME color. Colors: c=0/3 -> color0, c=1 -> color1,
        # c=2 -> color2. Decoded color equal iff codes match on this mapping.
        # Vertex u qubits:
        u0, u1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        v0, v1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        # color(u) == color(v) can be broken into the 3 color classes:
        #   both color0: (u in {00,11}) and (v in {00,11})
        #   both color1: u==01 and v==01
        #   both color2: u==10 and v==10
        # target ^= OR of these three disjoint AND-terms.
        pass

    # We need scratch ancillas. Use ancilla_qubits[0..2] for per-vertex color0
    # indicator and the two-vertex conjunction; ancilla_qubits[3] is the
    # predicate-accumulation flag. To respect budget, process edge-by-edge.
    #
    # Strategy: mark bit m (ancilla[3]) = number of monochromatic edges != 0.
    # f = 1 iff NO edge monochromatic, i.e. m stays 0. We flip phase on m==0,
    # implemented as X m -> Z-controlled... Instead: accumulate "bad" flag on
    # ancilla[3]; predicate satisfied iff ancilla[3]==0 -> phase via anti-control.
    #
    # For each edge we flip ancilla[3] once for each color-class match. Since
    # at most one class can match per edge, ancilla[3] parity == (#bad edges).
    # No edge shares... edges (0,1),(2,3),(3,4) share vertex 3 but that's fine,
    # each edge contributes independently to the parity flag.

    a_c0u = ancilla_qubits[0]  # scratch: u is color0 (code 00 or 11)
    a_c0v = ancilla_qubits[1]  # scratch: v is color0
    a_and = ancilla_qubits[2]  # scratch: conjunction
    bad = ancilla_qubits[3]    # accumulates parity of monochromatic edges

    def color0_indicator(v, out):
        # out ^= 1 iff vertex v code in {00, 11} (b0 == b1)
        v0, v1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        # b0==b1  <=>  NOT(b0 XOR b1)
        qc.cx(v0, out)
        qc.cx(v1, out)
        qc.x(out)  # now out ^= (b0 XNOR b1)

    def color0_indicator_un(v, out):
        v0, v1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        qc.x(out)
        qc.cx(v1, out)
        qc.cx(v0, out)

    for (u, v) in edges:
        u0, u1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        v0, v1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # --- class color0: both in {00,11} ---
        color0_indicator(u, a_c0u)
        color0_indicator(v, a_c0v)
        qc.ccx(a_c0u, a_c0v, bad)  # bad ^= both-color0
        color0_indicator_un(v, a_c0v)
        color0_indicator_un(u, a_c0u)

        # --- class color1: both == 01 (b0=1,b1=0) ---
        # u==01: u0 AND NOT u1 ; v==01: v0 AND NOT v1
        qc.x(u1)
        qc.x(v1)
        qc.ccx(u0, u1, a_c0u)          # a_c0u = (u==01)
        qc.ccx(v0, v1, a_c0v)          # a_c0v = (v==01)
        qc.ccx(a_c0u, a_c0v, bad)      # bad ^= both-color1
        qc.ccx(v0, v1, a_c0v)
        qc.ccx(u0, u1, a_c0u)
        qc.x(v1)
        qc.x(u1)

        # --- class color2: both == 10 (b0=0,b1=1) ---
        qc.x(u0)
        qc.x(v0)
        qc.ccx(u0, u1, a_c0u)          # a_c0u = (u==10)
        qc.ccx(v0, v1, a_c0v)          # a_c0v = (v==10)
        qc.ccx(a_c0u, a_c0v, bad)      # bad ^= both-color2
        qc.ccx(v0, v1, a_c0v)
        qc.ccx(u0, u1, a_c0u)
        qc.x(v0)
        qc.x(u0)

    # Now `bad` == parity of monochromatic edges. f(x)=1 iff bad==0 AND no edge
    # bad (parity 0 with at most 1 bad per edge means truly 0). Phase -1 when
    # predicate satisfied = when bad == 0.
    qc.x(bad)
    qc.z(bad)
    qc.x(bad)

    # Uncompute `bad` back to |0>.
    for (u, v) in reversed(edges):
        u0, u1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        v0, v1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        qc.x(u0)
        qc.x(v0)
        qc.ccx(u0, u1, a_c0u)
        qc.ccx(v0, v1, a_c0v)
        qc.ccx(a_c0u, a_c0v, bad)
        qc.ccx(v0, v1, a_c0v)
        qc.ccx(u0, u1, a_c0u)
        qc.x(v0)
        qc.x(u0)

        qc.x(u1)
        qc.x(v1)
        qc.ccx(u0, u1, a_c0u)
        qc.ccx(v0, v1, a_c0v)
        qc.ccx(a_c0u, a_c0v, bad)
        qc.ccx(v0, v1, a_c0v)
        qc.ccx(u0, u1, a_c0u)
        qc.x(v1)
        qc.x(u1)

        color0_indicator(u, a_c0u)
        color0_indicator(v, a_c0v)
        qc.ccx(a_c0u, a_c0v, bad)
        color0_indicator_un(v, a_c0v)
        color0_indicator_un(u, a_c0u)
