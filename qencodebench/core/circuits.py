"""Shared reversible-logic building blocks for reference oracles.

All helpers operate on an existing QuantumCircuit via integer qubit indices.
Families share these components: the mod-surjective color
equality comparator (F2/F5), the increment-based counter (F2-T3/F3/F5-T3) and
the constant adder (F4).
"""

from __future__ import annotations

import math

from qiskit import QuantumCircuit


def x_conjugate(qc: QuantumCircuit, qubits: list[int], pattern: list[int]):
    """X gates on qubits whose pattern bit is 0 (so pattern becomes all-1)."""
    for q, b in zip(qubits, pattern):
        if b == 0:
            qc.x(q)


def flag_on_pattern(qc: QuantumCircuit, controls: list[int],
                    pattern: list[int], target: int) -> None:
    """target ^= 1 iff controls match pattern (list of 0/1, same order)."""
    x_conjugate(qc, controls, pattern)
    if len(controls) == 0:
        qc.x(target)
    elif len(controls) == 1:
        qc.cx(controls[0], target)
    else:
        qc.mcx(controls, target)
    x_conjugate(qc, controls, pattern)


def phase_on_pattern(qc: QuantumCircuit, qubits: list[int],
                     pattern: list[int]) -> None:
    """Apply phase -1 to basis states where qubits match pattern (MCZ)."""
    x_conjugate(qc, qubits, pattern)
    if len(qubits) == 1:
        qc.z(qubits[0])
    else:
        qc.mcp(math.pi, qubits[:-1], qubits[-1])
    x_conjugate(qc, qubits, pattern)


def controlled_increment(qc: QuantumCircuit, controls: list[int],
                         reg: list[int]) -> None:
    """reg (little-endian) += 1 mod 2^len(reg), controlled on all controls=1."""
    for i in range(len(reg) - 1, 0, -1):
        qc.mcx(controls + reg[:i], reg[i])
    if len(controls) == 0:
        qc.x(reg[0])
    elif len(controls) == 1:
        qc.cx(controls[0], reg[0])
    else:
        qc.mcx(controls, reg[0])


def controlled_decrement(qc: QuantumCircuit, controls: list[int],
                         reg: list[int]) -> None:
    """Exact inverse of controlled_increment."""
    if len(controls) == 0:
        qc.x(reg[0])
    elif len(controls) == 1:
        qc.cx(controls[0], reg[0])
    else:
        qc.mcx(controls, reg[0])
    for i in range(1, len(reg)):
        qc.mcx(controls + reg[:i], reg[i])


def controlled_add_const(qc: QuantumCircuit, controls: list[int],
                         reg: list[int], c: int) -> None:
    """reg += c mod 2^len(reg), controlled.  Decomposed into per-set-bit
    increments on the sub-register [j:], which commute."""
    for j in range(len(reg)):
        if (c >> j) & 1:
            controlled_increment(qc, controls, reg[j:])


def controlled_sub_const(qc: QuantumCircuit, controls: list[int],
                         reg: list[int], c: int) -> None:
    for j in range(len(reg)):
        if (c >> j) & 1:
            controlled_decrement(qc, controls, reg[j:])


# ---------------------------------------------------------------------------
# Mod-surjective 2-bit color components (F2 / F5).
# Code: bits (b1, b0) -> color 0 for 00 and 11 (surjective 11 -> 0),
#       color 1 for 01, color 2 for 10.
# ---------------------------------------------------------------------------

def decode_color(code2: int) -> int:
    """Classical decoder for the surjective 2-bit color code (11 -> 0)."""
    return 0 if code2 == 0b11 else code2


def flag_colors_differ(qc: QuantumCircuit, u: tuple[int, int],
                       v: tuple[int, int], target: int) -> None:
    """target ^= 1 iff decoded colors of cells u and v DIFFER.

    u = (u0, u1) little-endian qubit indices of the cell (u0 = LSB), same for v.
    same_color = A or B where A = (u == v bitwise), B = (u0==u1 and v0==v1);
    A or B = A xor B xor (A and B), each term realised as one pattern-flag.
    """
    u0, u1 = u
    v0, v1 = v
    # Term A: bitwise equal.  Map v0 <- u0^v0, v1 <- u1^v1, flag on 00.
    qc.cx(u0, v0)
    qc.cx(u1, v1)
    flag_on_pattern(qc, [v0, v1], [0, 0], target)
    qc.cx(u1, v1)
    qc.cx(u0, v0)
    # Term B: u0==u1 and v0==v1.  Map u1 <- u0^u1, v1 <- v0^v1, flag on 00.
    qc.cx(u0, u1)
    qc.cx(v0, v1)
    flag_on_pattern(qc, [u1, v1], [0, 0], target)
    qc.cx(v0, v1)
    qc.cx(u0, u1)
    # Term A and B: u == v and u0==u1  (then v0==v1 is implied).
    qc.cx(u0, v0)
    qc.cx(u1, v1)
    qc.cx(u0, u1)
    flag_on_pattern(qc, [v0, v1, u1], [0, 0, 0], target)
    qc.cx(u0, u1)
    qc.cx(u1, v1)
    qc.cx(u0, v0)
    # target currently = same_color; flip to "differ".
    qc.x(target)


def flag_cell_differs_const(qc: QuantumCircuit, cell: tuple[int, int],
                            value: int, target: int) -> None:
    """target ^= 1 iff decoded color of cell DIFFERS from constant value."""
    c0, c1 = cell
    if value == 0:
        # equal to 0 iff c0 == c1: map c1 <- c0^c1, flag on 0.
        qc.cx(c0, c1)
        flag_on_pattern(qc, [c1], [0], target)
        qc.cx(c0, c1)
    elif value == 1:
        flag_on_pattern(qc, [c0, c1], [1, 0], target)   # code 01 (b0=1, b1=0)
    elif value == 2:
        flag_on_pattern(qc, [c0, c1], [0, 1], target)   # code 10
    else:
        raise ValueError(f"invalid color {value}")
    qc.x(target)


def counter_width(n_events: int) -> int:
    """Bits needed to count 0..n_events."""
    return max(1, math.ceil(math.log2(n_events + 1)))
