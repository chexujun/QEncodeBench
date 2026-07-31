import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    a = problem_qubits
    anc = ancilla_qubits
    # a = [1, 1, 3], target T = 2.
    # Solutions (x0,x1,x2): subsets summing to 2.
    #   x0+x1 = 2 with x2=0  -> (1,1,0)
    #   value 3 alone or with others exceeds/!=2, so only (1,1,0).
    # f(x)=1  iff  x0=1, x1=1, x2=0.
    qc.x(a[2])                      # compute NOT x2 into a[2] temporarily
    qc.ccx(a[0], a[1], anc[0])      # anc0 = x0 AND x1
    qc.ccx(anc[0], a[2], anc[1])    # anc1 = x0 AND x1 AND (NOT x2)
    qc.z(anc[1])                    # phase -1 on the single solution
    qc.ccx(anc[0], a[2], anc[1])    # uncompute anc1
    qc.ccx(a[0], a[1], anc[0])      # uncompute anc0
    qc.x(a[2])                      # restore x2
