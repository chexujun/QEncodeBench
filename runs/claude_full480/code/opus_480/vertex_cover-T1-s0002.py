from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    # ancillas: 4 edge-cover flags, 1 count>=3 flag, 1 combined predicate, 1 spare
    e01, e02, e12, e13 = ancilla_qubits[0:4]
    cnt_bad = ancilla_qubits[4]     # 1 iff popcount(x) >= 3
    pred = ancilla_qubits[5]        # 1 iff full predicate true

    edge_flags = [(e01, x0, x1), (e02, x0, x2), (e12, x1, x2), (e13, x1, x3)]

    # ---- compute edge-cover flags: flag = OR(u,v) = NOT(AND(NOT u, NOT v)) ----
    for flag, u, v in edge_flags:
        qc.x(u); qc.x(v)
        qc.ccx(u, v, flag)   # flag = (NOT u) AND (NOT v)  -> flag=1 means edge NOT covered
        qc.x(u); qc.x(v)
        qc.x(flag)           # flag = 1 iff edge covered

    # ---- compute cnt_bad = 1 iff at least 3 of the 4 bits are 1 ----
    # popcount>=3 means some triple among the 4 variables is all-1.
    # Use MCX for each 3-subset ORed onto cnt_bad. There are 4 triples.
    triples = [(x0, x1, x2), (x0, x1, x3), (x0, x2, x3), (x1, x2, x3)]
    # cnt_bad currently 0. OR of the triple-AND terms:
    # For >=3 ones, exactly the triples that are subsets of the on-set fire.
    # ORing them via successive mcx toggles would double-toggle when 4 ones.
    # popcount==4 -> all 4 triples fire -> even toggles -> cnt_bad wrong.
    # Handle robustly: cnt_bad = 1 iff (#triples fired) is odd OR any fired.
    # Instead compute directly: bad iff (majority). Use dedicated logic:
    # bad = (x0&x1&x2)|(x0&x1&x3)|(x0&x2&x3)|(x1&x2&x3).
    # Compute via inclusion using an extra spare ancilla as running OR is hard
    # with only toggles. Use: for 4 vars, popcount>=3 == NOT(popcount<=2).
    # Simplest exact toggle-safe route: set cnt_bad using the 4-var symmetric
    # function with controlled corrections.
    # ones>=3: toggle for each triple (parity), then fix the all-4 case.
    for a, b, c in triples:
        qc.ccx(a, b, cnt_bad)  # placeholder pattern replaced below
    # The above uses ccx incorrectly (needs 3 controls); redo properly:
    # (undo the wrong ccx toggles)
    for a, b, c in triples:
        qc.ccx(a, b, cnt_bad)
    # Now cnt_bad is back to 0. Do it correctly with mcx (3 controls):
    for a, b, c in triples:
        qc.mcx([a, b, c], cnt_bad)
    # parity of fired triples: popcount3->1 triple(odd->1), popcount4->4 triples(even->0)
    # fix popcount==4: toggle cnt_bad once when all four are 1
    qc.mcx([x0, x1, x2, x3], cnt_bad)  # now popcount4 -> cnt_bad=1 as well

    # ---- pred = (all edges covered) AND (NOT cnt_bad) ----
    qc.x(cnt_bad)  # cnt_bad' = 1 iff popcount <= 2
    qc.mcx([e01, e02, e12, e13, cnt_bad], pred)
    qc.x(cnt_bad)  # restore cnt_bad

    # ---- phase ----
    qc.z(pred)

    # ---- uncompute pred ----
    qc.x(cnt_bad)
    qc.mcx([e01, e02, e12, e13, cnt_bad], pred)
    qc.x(cnt_bad)

    # ---- uncompute cnt_bad (mirror) ----
    qc.mcx([x0, x1, x2, x3], cnt_bad)
    for a, b, c in reversed(triples):
        qc.mcx([a, b, c], cnt_bad)

    # ---- uncompute edge-cover flags (mirror) ----
    for flag, u, v in reversed(edge_flags):
        qc.x(flag)
        qc.x(u); qc.x(v)
        qc.ccx(u, v, flag)
        qc.x(u); qc.x(v)
