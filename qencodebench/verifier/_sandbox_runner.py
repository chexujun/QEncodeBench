"""Child-process runner: build the candidate circuit from untrusted code.

Reads a JSON job from stdin: {"code", "n_problem", "n_total", "qpy_path"}.
Writes a JSON result to stdout: {"ok", "width", "error"}.
The circuit is serialized to qpy_path on success.

This is a best-effort research sandbox (subprocess + rlimits + timeout at
the parent), not a security boundary.
"""

import json
import resource
import sys
import traceback

MEM_LIMIT_BYTES = 2 * 1024 ** 3


def main() -> None:
    job = json.load(sys.stdin)
    for rlimit in (resource.RLIMIT_AS, resource.RLIMIT_DATA):
        try:
            resource.setrlimit(rlimit, (MEM_LIMIT_BYTES, MEM_LIMIT_BYTES))
        except (ValueError, OSError):
            pass

    from qiskit import QuantumCircuit, qpy

    namespace: dict = {"__name__": "__qeb_sandbox__"}
    try:
        exec(compile(job["code"], "<candidate>", "exec"), namespace)
        fn = namespace.get("build_oracle")
        if fn is None:
            raise NameError("build_oracle is not defined at module level")
        n_problem, n_total = job["n_problem"], job["n_total"]
        qc = QuantumCircuit(n_total)
        fn(qc, list(range(n_problem)), list(range(n_problem, n_total)))
        with open(job["qpy_path"], "wb") as fh:
            qpy.dump(qc, fh)
        print(json.dumps({"ok": True, "width": qc.num_qubits, "error": None}))
    except BaseException:
        tb = traceback.format_exc(limit=5)
        print(json.dumps({"ok": False, "width": None, "error": tb[-2000:]}))


if __name__ == "__main__":
    main()
