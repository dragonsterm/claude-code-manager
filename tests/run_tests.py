# Minimal stdlib test runner (no pytest available in this env).
# ponytail: hand-rolled runner; replace with `python -m pytest` once pytest is installed.
import importlib
import inspect
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

MODULES = ("tests.test_app_state", "tests.test_launcher")


def main():
    ok = fail = 0
    for name in MODULES:
        mod = importlib.import_module(name)
        for attr, fn in vars(mod).items():
            if not attr.startswith("test_") or not callable(fn):
                continue
            args = []
            if "tmp_path" in inspect.signature(fn).parameters:
                args = [pathlib.Path(tempfile.mkdtemp())]
            try:
                fn(*args)
                ok += 1
                print("PASS", name, attr)
            except Exception as exc:  # noqa: BLE001 - report and continue
                fail += 1
                print("FAIL", name, attr, repr(exc))
    print(str(ok) + " passed, " + str(fail) + " failed")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
