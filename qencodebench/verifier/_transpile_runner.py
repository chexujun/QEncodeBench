"""Child-process transpile for L4 on simulation-risk circuits: the fixed
basis synthesis of very wide multi-controlled gates can be slow enough to
stall the verifier, so risky circuits get a wall-clock-guarded child."""

import json
import sys


def main() -> None:
    job = json.load(sys.stdin)
    from qiskit import qpy
    from qencodebench.core.transpiling import transpile_fixed

    with open(job["qpy_path"], "rb") as fh:
        circ = qpy.load(fh)[0]
    print("QEB_L4:" + json.dumps({"depth": transpile_fixed(circ).depth()}))


if __name__ == "__main__":
    main()
