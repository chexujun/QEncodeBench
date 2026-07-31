from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (1, 2), (1, 3), (1, 5), (2, 4), (2, 5), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # Ancillas: e = per-edge "same color" flag (reused), acc = AND accumulator
    e = ancilla_qubits[0]
    acc = ancilla_qubits[1]
    t0 = ancilla_qubits[2]
    t1 = ancilla_qubits[3]

    def edge_same(u, v, out):
        # out ^= [color(u) == color(v)]
        # color equality with surjective decode: c=3 -> color 0.
        # Effective color equal iff (a==b) OR (one is 00 and other is 11)
        #   i.e. codes {00,11} both map to color0, {01}->1, {10}->2.
        # color(u)==color(v) iff:
        #   (both in {00,11}) OR (both ==01) OR (both ==10)
        au0, au1 = qb(u)
        av0, av1 = qb(v)
        # Compute t0 = [u in {00,11}] = (au0 == au1) = NOT(au0 xor au1)
        qc.cx(au0, t0)
        qc.cx(au1, t0)
        qc.x(t0)  # t0 = 1 iff au0==au1 (color0 for u)
        # t1 = [v in {00,11}]
        qc.cx(av0, t1)
        qc.cx(av1, t1)
        qc.x(t1)
        # term A: both color0 -> out ^= t0 & t1
        qc.ccx(t0, t1, out)
        # term B: both ==01 (au0=1,au1=0)&(av0=1,av1=0) -> color1
        qc.x(au1)
        qc.x(av1)
        qc.mcx([au0, au1, av0, av1], out)
        qc.x(au1)
        qc.x(av1)
        # term C: both ==10 (au0=0,au1=1)&(av0=0,av1=1) -> color2
        qc.x(au0)
        qc.x(av0)
        qc.mcx([au0, au1, av0, av1], out)
        qc.x(au0)
        qc.x(av0)
        # uncompute t0,t1
        qc.x(t1)
        qc.cx(av1, t1)
        qc.cx(av0, t1)
        qc.x(t0)
        qc.cx(au1, t0)
        qc.cx(au0, t0)

    # acc counts violated edges via: we want f=1 iff NO edge is same-color.
    # Build acc = OR of all edge_same flags, then phase on acc==0.
    # We accumulate OR into acc by toggling e per edge and OR-ing.
    # Use acc as running OR: acc = acc OR e, with e freshly computed each edge.
    for (u, v) in edges:
        edge_same(u, v, e)          # e = same-color flag for this edge
        # acc = acc OR e  ==>  acc = NOT( NOT acc AND NOT e )
        qc.x(acc)
        qc.x(e)
        qc.ccx(e, acc, acc)  # if e==1(after x meaning orig 0)... careful
        qc.x(e)
        qc.x(acc)
        edge_same(u, v, e)          # uncompute e back to 0
