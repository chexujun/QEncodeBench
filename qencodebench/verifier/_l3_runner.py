"""Child-process L3 functional verification (wall-clock isolatable).

Reads a JSON job from stdin: {"qpy_path", "n_problem", "task_id",
"solutions", "sample_key", "force_exhaustive"}; prints one JSON line:
the FuncResult fields.  Used for circuits flagged as simulation risks
(huge gate counts or very wide multi-controlled instructions) so that a
pathological decomposition/simulation cannot hang the verifier -- the
parent enforces a timeout and records TIMEOUT.
"""

import dataclasses
import json
import sys


def main() -> None:
    job = json.load(sys.stdin)
    from qiskit import qpy
    from qencodebench.verifier.verify import verify_circuit

    with open(job["qpy_path"], "rb") as fh:
        circ = qpy.load(fh)[0]
    from qencodebench.verifier.verify import VerifierInconsistency
    try:
        res = verify_circuit(
            circ, job["n_problem"], job["task_id"],
            set(job["solutions"]), sample_key=job["sample_key"],
            force_exhaustive=job.get("force_exhaustive", False),
        )
    except VerifierInconsistency as e:
        # freeze semantics must survive the process boundary
        print("QEB_L3_FREEZE:" + str(e))
        return
    print("QEB_L3:" + json.dumps(dataclasses.asdict(res)))


if __name__ == "__main__":
    main()
