"""Installation and repository-layout sanity checks for MW-SR.

Run from the repository root with either:

    python tests/test_installation.py
    python -m pytest tests/test_installation.py

The checks intentionally stay lightweight: they verify that required packages
can be imported, the local MW-SR package is importable after installation, and
important files are stored in the expected repository folders.
"""
from __future__ import annotations

import importlib
import importlib.metadata as metadata
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Dependency:
    import_name: str
    package_name: str
    required: bool = True


DEPENDENCIES = (
    Dependency("numpy", "numpy"),
    Dependency("h5py", "h5py"),
    Dependency("matplotlib", "matplotlib"),
    Dependency("yaml", "PyYAML"),
    Dependency("skimage", "scikit-image"),
    Dependency("tensorflow", "tensorflow"),
    Dependency("mw_super_resolution", "mw-sr"),
    Dependency("jupyterlab", "jupyterlab"),
    Dependency("notebook", "notebook"),
    Dependency("ipykernel", "ipykernel"),
    Dependency("pandas", "pandas", required=False),
    Dependency("sklearn", "scikit-learn", required=False),
    Dependency("pytest", "pytest"),
)

RELATED_TEST_FILES = (
    "tests/test_loader.py",
    "tests/test_models.py",
    "tests/test_release_artifacts.py",
    "tests/test_sample_data.py",
)

REQUIRED_PATHS = (
    "README.md",
    "environment.yml",
    "pyproject.toml",
    "configs/mw_sr.yaml",
    "configs/mw_sr_gan.yaml",
    "metadata/unified_global_stats.json",
    "sample_data/amsr2_example.h5",
    "src/mw_super_resolution/__init__.py",
    "src/mw_super_resolution/loader.py",
    "src/mw_super_resolution/normalization.py",
    "scripts/inference/make_prediction.py",
    "scripts/evaluation/metrics.py",
    "scripts/evaluation/plot_predictions.py",
    "scripts/evaluation/plot_selected_model_residuals.py",
    "scripts/training/train_rrdn.py",
    "scripts/training/train_gan.py",
    "tools/inspect_h5_files.py",
)

APPROVED_MODEL_ARTIFACT_DIRS = (
    Path("release_assets"),
    Path("legacy/checkpoints"),
)

APPROVED_HDF5_DATA_DIRS = (
    Path("sample_data"),
    Path("AMSR2"),
    Path("ATMS"),
    Path("tomorrow.io.new"),
    Path("github_case/data"),
    Path("outputs"),
    Path("legacy/checkpoints"),
)

APPROVED_CODE_DIRS = (
    Path("src"),
    Path("scripts"),
    Path("tools"),
    Path("tests"),
    Path("github_case"),
    Path("legacy/model_definitions"),
)

IGNORED_DIR_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ipynb_checkpoints",
    "mw_sr.egg-info",
}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def is_ignored_path(path: Path) -> bool:
    return any(part in IGNORED_DIR_PARTS for part in path.parts)


def check_dependency(dep: Dependency) -> tuple[str, str | None, str | None]:
    """Return package name, version if available, and an error message if import fails."""
    if dep.import_name == "mw_super_resolution":
        src_path = repository_root() / "src"
        if src_path.exists() and str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

    try:
        importlib.import_module(dep.import_name)
    except Exception as exc:  # pragma: no cover - exercised only in broken envs.
        return dep.package_name, None, f"{type(exc).__name__}: {exc}"

    try:
        version = metadata.version(dep.package_name)
    except metadata.PackageNotFoundError:
        version = "installed; version metadata not found"
    return dep.package_name, version, None


def collect_installation_status() -> list[tuple[Dependency, str | None, str | None]]:
    status = []
    for dep in DEPENDENCIES:
        _package_name, version, error = check_dependency(dep)
        status.append((dep, version, error))
    return status


def collect_layout_status(root: Path) -> dict[str, list[str]]:
    missing_required = [rel for rel in REQUIRED_PATHS if not (root / rel).exists()]

    misplaced_model_artifacts: list[str] = []
    misplaced_hdf5_data: list[str] = []
    misplaced_code: list[str] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(root)
        if is_ignored_path(rel):
            continue

        is_model_artifact = file_path.name.endswith((".keras", ".weights.h5"))
        is_hdf5 = file_path.name.endswith((".h5", ".hdf5"))
        is_python = file_path.suffix == ".py"

        if is_model_artifact:
            if not any(is_under(rel, approved) for approved in APPROVED_MODEL_ARTIFACT_DIRS):
                misplaced_model_artifacts.append(str(rel))
        elif is_hdf5 and not any(is_under(rel, approved) for approved in APPROVED_HDF5_DATA_DIRS):
            misplaced_hdf5_data.append(str(rel))

        if is_python and not any(is_under(rel, approved) for approved in APPROVED_CODE_DIRS):
            misplaced_code.append(str(rel))

    return {
        "missing_required": sorted(missing_required),
        "misplaced_model_artifacts": sorted(misplaced_model_artifacts),
        "misplaced_hdf5_data": sorted(misplaced_hdf5_data),
        "misplaced_code": sorted(misplaced_code),
    }


def test_required_dependencies_importable() -> None:
    status = collect_installation_status()
    missing_required = [
        f"{dep.package_name} ({dep.import_name}) -> {error}"
        for dep, _version, error in status
        if dep.required and error is not None
    ]
    assert not missing_required, (
        "Missing required MW-SR dependencies:\n"
        + "\n".join(f"- {item}" for item in missing_required)
        + "\n\nInstall with:\n"
        + "conda env update -f environment.yml --prune\n"
        + "conda activate MW-SR-Env\n"
        + "python -m pip install -e ."
    )


def test_repository_files_are_in_expected_directories() -> None:
    status = collect_layout_status(repository_root())
    problems = []
    for label, items in status.items():
        if items:
            problems.append(label + ":\n" + "\n".join(f"- {item}" for item in items))
    assert not problems, "Repository layout problems found:\n\n" + "\n\n".join(problems)


def run_related_project_tests(root: Path) -> subprocess.CompletedProcess[str]:
    src_path = root / "src"
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_path) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
    env.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "mw-sr-mplconfig"))
    Path(env["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, "-m", "pytest", "-q", *RELATED_TEST_FILES]
    return subprocess.run(cmd, cwd=root, env=env, text=True, capture_output=True, check=False)


def test_related_project_tests_pass() -> None:
    result = run_related_project_tests(repository_root())
    assert result.returncode == 0, (
        "Related MW-SR test files failed:\n"
        + " ".join(RELATED_TEST_FILES)
        + "\n\nSTDOUT:\n"
        + result.stdout
        + "\nSTDERR:\n"
        + result.stderr
    )


def main() -> int:
    root = repository_root()
    install_status = collect_installation_status()
    layout_status = collect_layout_status(root)
    missing_required = []
    layout_problems = {key: items for key, items in layout_status.items() if items}
    related_test_result: subprocess.CompletedProcess[str] | None = None

    print("MW-SR installation check")
    print("=" * 24)
    for dep, version, error in install_status:
        label = "required" if dep.required else "optional"
        if error is None:
            print(f"[OK]   {dep.package_name:<16} {version} ({label})")
        else:
            print(f"[MISS] {dep.package_name:<16} {error} ({label})")
            if dep.required:
                missing_required.append(dep)

    print("\nMW-SR repository layout check")
    print("=" * 29)
    if layout_problems:
        for label, items in layout_problems.items():
            print(f"[MISS] {label}")
            for item in items:
                print(f"       - {item}")
    else:
        print("[OK]   Required weights, data, metadata, configs, and code are in expected directories.")

    if not missing_required and not layout_problems:
        print("\nMW-SR related test check")
        print("=" * 26)
        print("Running: python -m pytest -q " + " ".join(RELATED_TEST_FILES))
        related_test_result = run_related_project_tests(root)
        if related_test_result.stdout:
            print(related_test_result.stdout, end="")
        if related_test_result.stderr:
            print(related_test_result.stderr, end="", file=sys.stderr)
        if related_test_result.returncode == 0:
            print("[OK]   Related MW-SR tests passed.")
        else:
            print("[MISS] Related MW-SR tests failed.")

    if missing_required:
        print("\nRequired dependencies are missing. From the repository root, run:")
        print("  conda env update -f environment.yml --prune")
        print("  conda activate MW-SR-Env")
        print("  python -m pip install -e .")

    if missing_required or layout_problems or (related_test_result is not None and related_test_result.returncode != 0):
        return 1

    print("\nAll required MW-SR dependencies are importable, the repository layout looks correct, and related tests pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
