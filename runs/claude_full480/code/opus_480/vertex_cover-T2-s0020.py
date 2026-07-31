import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    edges = [(0, 2), (0, 4), (1, 3), (2, 3), (3, 4)]

    # Ancilla layout:
    # a_edges[0..4]  -> one ancilla per edge, flagged when edge is covered
    # cnt3           -> flag: popcount(x) <= 3  (i.e. NOT (>=4 ones))
    # flag           -> combined predicate ancilla for the phase
    a_edges = ancilla_qubits[0:5]
    cnt3 = ancilla_qubits[5]
    flag = ancilla_qubits[6]

    def compute_edges():
        # edge covered = OR(u, v) = NOT( (NOT u) AND (NOT v) )
        for (u, v), a in zip(edges, a_edges):
            qc.x(x[u]); qc.x(x[v])
            qc.ccx(x[u], x[v], a)   # a = (NOT u)AND(NOT v) after the surrounding x's
            qc.x(a)                 # a = OR(u,v)
            qc.x(x[u]); qc.x(x[v])

    def uncompute_edges():
        for (u, v), a in zip(reversed(edges), reversed(a_edges)):
            qc.x(x[u]); qc.x(x[v])
            qc.x(a)
            qc.ccx(x[u], x[v], a)
            qc.x(x[u]); qc.x(x[v])

    def compute_cnt3():
        # cnt3 = 1  iff  number of ones among the 5 problem qubits <= 3
        # equivalently cnt3 = NOT( at least 4 of the 5 are 1 ).
        # "at least 4 of 5" = OR over the 5 ways to pick 4 qubits all being 1.
        # Compute each 4-subset AND into cnt3 via toggling, then invert.
        subsets = [
            [0, 1, 2, 3],
            [0, 1, 2, 4],
            [0, 1, 3, 4],
            [0, 2, 3, 4],
            [1, 2, 3, 4],
        ]
        # These 5 subsets are mutually exclusive as "exactly this 4-set all-ones"
        # only overlap when all 5 are ones; handle by using cnt3 as OR flag.
        # Build OR via: cnt3 currently 0; for each subset set cnt3=1 if all ones.
        # Since we cannot cleanly OR into one ancilla with mcx (would toggle),
        # use inclusion: with all-5-ones, an odd/even count matters. To avoid
        # that, gate each subset on "the excluded qubit is 0".
        # subset i excludes qubit i.
        for i, s in enumerate(subsets):
            excluded = i
            qc.x(x[excluded])
            qc.mcx([x[excluded]] + [x[j] for j in s], cnt3)
            qc.x(x[excluded])
        # now cnt3 = 1 iff exactly-4-ones (some qubit is 0 and the other 4 are 1).
        # If all 5 are ones, none of the guarded terms fired, cnt3 stays 0.
        # We want cnt3 = (popcount <= 3):
        #   popcount<=3 true  -> currently cnt3=0 (no 4-subset all ones) -> need 1
        #   popcount==4       -> currently cnt3=1 -> need 0
        #   popcount==5       -> currently cnt3=0 -> need 0
        # So flip, then subtract the all-5 case.
        qc.x(cnt3)  # cnt3 = 1 for <=3 and for ==5 ; 0 for ==4
        # remove the all-5-ones case: if all 5 ones, force cnt3 -> 0
        qc.mcx([x[j] for j in range(5)], cnt3)

    def uncompute_cnt3():
        qc.mcx([x[j] for j in range(5)], cnt3)
        qc.x(cnt3)
        subsets = [
            [0, 1, 2, 3],
            [0, 1, 2, 4],
            [0, 1, 3, 4],
            [0, 2, 3, 4],
            [1, 2, 3, 4],
        ]
        for i in reversed(range(len(subsets))):
            s = subsets[i]
            excluded = i
            qc.x(x[excluded])
            qc.mcx([x[excluded]] + [x[j] for j in s], cnt3)
            qc.x(x[excluded])

    # ---- compute predicate ----
    compute_edges()
    compute_cnt3()

    # flag = AND(all edges covered) AND cnt3
    controls = list(a_edges) + [cnt3]
    qc.mcx(controls, flag)

    # phase
    qc.z(flag)

    # uncompute flag
    qc.mcx(controls, flag)

    uncompute_cnt3()
    uncompute_edges()
