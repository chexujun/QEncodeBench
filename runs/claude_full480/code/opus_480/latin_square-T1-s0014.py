from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: (0,0) -> cell 0, (2,2) -> cell 1
    # Grid:
    #   . 2 1        (0,0)=A
    #   2 1 0
    #   1 0 .        (2,2)=B
    #
    # Row0 fixed {2,1}, so A must = 0.
    # Col0 fixed {2,1}, so A must = 0.  -> A == 0 (value 0)
    # Row2 fixed {1,0}, so B must = 2.
    # Col2 fixed {1,0}, so B must = 2.  -> B == 2 (value 2)
    #
    # Values: code -> value: 00->0, 01->1, 10->2, 11->0
    # A value 0 <=> code in {00, 11} <=> b0 == b1 (a0 == a1)
    # B value 2 <=> code == 10 <=> b0==0 and b1==1
    #
    # a0=problem_qubits[0], a1=problem_qubits[1]
    # b0=problem_qubits[2], b1=problem_qubits[3]
    a0, a1 = problem_qubits[0], problem_qubits[1]
    b0, b1 = problem_qubits[2], problem_qubits[3]
    anc = ancilla_qubits[0]

    # Predicate = (a0 == a1) AND (b0 == 0) AND (b1 == 1)
    # Build controls that are all-1 when predicate holds:
    #   want (a0 XOR a1) == 0  -> compute t_a = NOT(a0 XOR a1)
    #   want b0 == 0           -> control on NOT b0
    #   want b1 == 1           -> control on b1
    # Use ancilla to hold NOT(a0 XOR a1).
    ta = ancilla_qubits[1]

    # compute ta = 1 iff a0 == a1
    qc.cx(a0, ta)
    qc.cx(a1, ta)
    qc.x(ta)   # ta = NOT(a0 xor a1)

    # b0 == 0: temporarily flip b0 so control-on-1 means original 0
    qc.x(b0)

    # phase: -1 iff ta==1 and b0(flipped)==1 and b1==1
    qc.h(anc)
    qc.x(anc)
    # multi-controlled X onto anc gives phase kickback via H; simpler: use mcp
    qc.x(anc)
    qc.h(anc)
    # (reset the above no-op scaffolding) -- use mcp for clean phase:
    qc.mcp(math.pi, [ta, b0, b1], anc) if False else qc.h(anc)
    qc.h(anc)

    # Clean approach: apply controlled-Z equivalent via mcp on the controls directly.
    qc.mcp(math.pi, [ta, b0], b1)

    # uncompute
    qc.x(b0)
    qc.x(ta)
    qc.cx(a1, ta)
    qc.cx(a0, ta)
