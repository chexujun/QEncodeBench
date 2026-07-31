import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 5)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    su0, su1, eq = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    flags = [ancilla_qubits[3], ancilla_qubits[4]]

    def xor_decode0(v, t):
        b0, b1 = qb(v)
        qc.x(b1); qc.ccx(b0, b1, t); qc.x(b1)

    def xor_decode1(v, t):
        b0, b1 = qb(v)
        qc.x(b0); qc.ccx(b1, b0, t); qc.x(b0)

    def compute_eq(u, v):
        xor_decode0(u, su0); xor_decode0(v, su0)
        xor_decode1(u, su1); xor_decode1(v, su1)
        qc.x(su0); qc.x(su1)
        qc.ccx(su0, su1, eq)          # eq = colors_equal
        qc.x(su1); qc.x(su0)

    def uncompute_eq(u, v):
        qc.x(su0); qc.x(su1)
        qc.ccx(su0, su1, eq)
        qc.x(su1); qc.x(su0)
        xor_decode1(v, su1); xor_decode1(u, su1)
        xor_decode0(v, su0); xor_decode0(u, su0)

    n = len(edges)

    # Recursive fold: flag_{k} = flag_{k-1} AND (NOT eq_k), with flag_0 = 1.
    # We need flag_n on a qubit, then Z it, then uncompute everything.
    # Use two flag ancillas ping-ponging; uncompute each stage in reverse.
    # Build forward computing into a stack, then apply Z, then reverse.

    # Forward pass: at step k, cur = flags[k%2], prev = flags[(k-1)%2].
    # cur = prev AND NOT eq_k  (cur starts |0>). Keep eq_k alive? We must
    # uncompute eq_k only in reverse to be able to restore prev, so we keep
    # eq computed and stored... but only one eq ancilla. So we cannot keep
    # all eq. Therefore uncompute eq_k immediately after using it; that's
    # fine because cur depends only on prev and eq_k, and to reverse we
    # recompute eq_k. Standard reversible fold.

    qc.x(flags[0])  # flag_0 = 1
    parity = 0
    for k in range(n):
        u, v = edges[k]
        prev = flags[k % 2]
        cur = flags[(k + 1) % 2]
        compute_eq(u, v)
        qc.x(eq)
        qc.ccx(prev, eq, cur)        # cur = prev AND NOT eq
        qc.x(eq)
        uncompute_eq(u, v)
    # flag_n on flags[n % 2]
    qc.z(flags[n % 2])
    # reverse
    for k in reversed(range(n)):
        u, v = edges[k]
        prev = flags[k % 2]
        cur = flags[(k + 1) % 2]
        compute_eq(u, v)
        qc.x(eq)
        qc.ccx(prev, eq, cur)
        qc.x(eq)
        uncompute_eq(u, v)
    qc.x(flags[0])
