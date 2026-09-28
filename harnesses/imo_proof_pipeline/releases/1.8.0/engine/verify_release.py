"""Create and verify a local, content-locked Python harness release.

This packaging utility never invokes a model, solver, or experiment. Reference
artifacts are copied separately from importable source. Existing releases are
never overwritten. Model weights and the system environment are not bundled.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
import zipfile


SOURCE_SUFFIXES = {".py", ".md", ".json", ".toml", ".yaml", ".yml", ".txt", ".sh", ".lib"}
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".git", "runs", ".env"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_file(path, root):
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Symlink or escaped source: {path}")
    return path.is_file() and not (set(path.relative_to(root).parts) & EXCLUDED_PARTS)


def sources(root, package):
    """Static local-import closure, including all modules in the target package.

    No source module is executed. Literal importlib imports are also followed;
    genuinely computed imports still require an offline smoke test of the copy.
    """
    included, pending, expanded, external = set(), [], set(), set()

    def add(path):
        if path not in included and safe_file(path, root):
            included.add(path)
            if path.suffix == ".py":
                pending.append(path)
            for parent in path.parents:
                if parent == root:
                    break
                init = parent / "__init__.py"
                if init.is_file() and init != path:
                    add(init)

    def resolve(name):
        if not name or any(not part.isidentifier() for part in name.split(".")):
            return
        top = name.split(".")[0]
        if top == package and (root / top).is_dir():
            if top not in expanded:
                expanded.add(top)
                for path in sorted((root / top).rglob("*")):
                    if path.suffix in SOURCE_SUFFIXES:
                        add(path)
        candidate = root.joinpath(*name.split("."))
        if candidate.with_suffix(".py").is_file():
            add(candidate.with_suffix(".py"))
        elif (candidate / "__init__.py").is_file():
            add(candidate / "__init__.py")
        elif "." not in name and (root / "scripts" / (name + ".py")).is_file():
            add(root / "scripts" / (name + ".py"))
        elif not (root / top).exists():
            external.add(top)

    if not (root / package / "__init__.py").is_file():
        raise ValueError("Expected a local Python package")
    resolve(package)
    while pending:
        path = pending.pop()
        parts = list(path.relative_to(root).with_suffix("").parts)
        owner = parts[:-1]
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    resolve(alias.name)
            elif isinstance(node, ast.ImportFrom):
                prefix = owner[:len(owner) - node.level + 1] if node.level else []
                name = ".".join(prefix + ([node.module] if node.module else []))
                resolve(name)
                for alias in node.names:
                    resolve(".".join(filter(None, (name, alias.name))))
            elif isinstance(node, ast.Call) and node.args:
                function = node.func
                name = function.attr if isinstance(function, ast.Attribute) else getattr(function, "id", "")
                arg = node.args[0]
                if name in {"import_module", "__import__"} and isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    resolve(arg.value)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                # Deferred subprocess module names and __package__ + '.worker'.
                value = node.value
                if value.startswith("cognitive_well_harness_") and (root / value.split(".")[0]).is_dir():
                    resolve(value)
                elif value.startswith(".") and value[1:].isidentifier():
                    resolve(".".join(owner) + value)
                # Repository-owned prompt/schema assets used by shared modules.
                if len(value) < 512 and "\n" not in value:
                    asset = Path(value)
                    if (asset.parts and asset.parts[0] in {"prompts", "schemas"}
                            and asset.suffix in SOURCE_SUFFIXES):
                        add(root / asset)
    return sorted(included), sorted(external - set(sys.stdlib_module_names))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def environment():
    versions = {}
    for package in ("sympy", "mpmath", "numpy", "requests", "httpx", "pytest"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    singular = shutil.which("Singular")
    return {"python": sys.version, "python_executable": sys.executable,
            "platform": platform.platform(), "packages": versions,
            "Singular_path": singular,
            "Singular_version": subprocess.run([singular, "--version"], capture_output=True, text=True, check=True).stdout if singular else None,
            "model_weights_bundled": False, "environment_is_observation_not_install_lock": True}


def build(root, package, run, config, output, release_id, extras, vendor_trees=(), profile=None):
    files, external = sources(root, package)
    result = {}
    if run is not None:
        result = json.loads((run / "result.json").read_text())
        if result.get("state") != "completed":
            raise ValueError("Reference experiment must have completed")
        if config is None:
            raise ValueError("A reference run requires its config")
    elif config is not None:
        raise ValueError("A reference config requires its run; use profile for source-only releases")
    archive_path = output.with_suffix(".zip")
    if archive_path.exists():
        raise FileExistsError(archive_path)
    output.mkdir(parents=True, exist_ok=False)
    hashes, executable_modes, materialized_links = {}, {}, {}

    def copy(path, destination):
        before = digest(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        shutil.copymode(path, destination)
        if digest(destination) != before or digest(path) != before:
            raise ValueError(f"Source changed during freeze: {path}")
        hashes[str(destination.relative_to(output))] = before
        if path.stat().st_mode & 0o111:
            executable_modes[str(destination.relative_to(output))] = path.stat().st_mode & 0o111

    for path in files:
        copy(path, output / "source" / path.relative_to(root))
    for tree in vendor_trees:
        if not tree.is_relative_to(root) or tree == root or not tree.is_dir():
            raise ValueError(f"Expected a scoped local vendor directory: {tree}")
        for path in sorted(tree.rglob("*")):
            if path.is_dir():
                if path.is_symlink():
                    raise ValueError(f"Directory symlinks require explicit packaging: {path}")
                continue
            resolved = path.resolve()
            if not resolved.is_relative_to(tree) or not resolved.is_file():
                raise ValueError(f"Vendor link escaped its directory: {path}")
            destination = output / "source" / path.relative_to(root)
            copy(resolved, destination)
            if path.is_symlink():
                materialized_links[str(destination.relative_to(output))] = str(resolved.relative_to(root))
    if run is not None:
        for path in sorted(run.rglob("*")):
            if safe_file(path, run):
                copy(path, output / "reference" / "run" / path.relative_to(run))
        copy(config, output / "reference" / "experiment.config.json")
    copy(Path(__file__).resolve(), output / "verify_release.py")
    for path in extras:
        if not safe_file(path, root):
            raise ValueError(f"Unsafe extra: {path}")
        copy(path, output / "release_notes" / path.name)
    # Effective runtime settings, with no problem, proof, gold or certificate.
    manifests = sorted(run.glob("*/rewrite/manifest.json")) if run else []
    if profile is not None:
        json.loads(profile.read_text())  # Reject invalid metadata before copying it.
        copy(profile, output / "runtime_profile.json")
    elif len(manifests) == 1:
        manifest = json.loads(manifests[0].read_text())
        write_json(output / "runtime_profile.json", manifest["config"])
        hashes["runtime_profile.json"] = digest(output / "runtime_profile.json")
    write_json(output / "environment.json", environment())
    hashes["environment.json"] = digest(output / "environment.json")
    lock = {"schema": "local-harness-source-freeze-v1", "release_id": release_id,
            "created_at": datetime.now(timezone.utc).isoformat(), "package": package,
            "source_policy": "target_package_plus_static_and_literal_deferred_import_closure",
            "unbundled_import_roots": external, "source_file_count": len(files),
            "release_kind": "source_and_reference" if run else "source_only",
            "reference_run": str(run) if run else None, "reference_scores": result.get("score_vector"),
            "reference_artifacts_are_not_generation_inputs": True,
            "model_output_contract_changed": False, "source_files_changed": False,
            "vendor_trees": [str(path.relative_to(root)) for path in vendor_trees],
            "materialized_vendor_links": materialized_links, "executable_modes": executable_modes,
            "files": hashes}
    write_json(output / "freeze.json", lock)
    checksum_files = sorted([*hashes, "freeze.json"])
    (output / "SHA256SUMS").write_text("".join(f"{digest(output / name)}  {name}\n" for name in checksum_files))
    verify(output)
    with zipfile.ZipFile(archive_path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=str(Path(output.name) / path.relative_to(output)))
    return {"release": str(output), "archive": str(archive_path), "archive_sha256": digest(archive_path),
            "source_file_count": len(files), "locked_file_count": len(hashes), "verified": True}


def verify(output):
    lock = json.loads((output / "freeze.json").read_text())
    expected = set(lock["files"]) | {"freeze.json", "SHA256SUMS"}
    actual = {str(path.relative_to(output)) for path in output.rglob("*") if path.is_file()}
    if expected != actual:
        raise ValueError(f"Unlisted/missing release files: {sorted(expected ^ actual)}")
    for name, expected_hash in lock["files"].items():
        path = output / name
        if not safe_file(path, output) or digest(path) != expected_hash:
            raise ValueError(f"Release checksum mismatch: {name}")
    for name, mode in lock.get("executable_modes", {}).items():
        if (output / name).stat().st_mode & 0o111 != mode:
            raise ValueError(f"Release executable mode mismatch: {name}")
    for line in (output / "SHA256SUMS").read_text().splitlines():
        expected_hash, name = line.split("  ", 1)
        path = output / name
        if not safe_file(path, output) or digest(path) != expected_hash:
            raise ValueError(f"Release checksum mismatch: {name}")
    return {"verified": True, "release_id": lock["release_id"], "files": len(lock["files"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--package")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--run", type=Path)
    parser.add_argument("--source-only", action="store_true", help="Freeze code without claiming a completed reference run")
    parser.add_argument("--profile", type=Path, help="Explicit non-problem runtime metadata to preserve")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--release-id")
    parser.add_argument("--extra", type=Path, action="append", default=[])
    parser.add_argument("--vendor-tree", type=Path, action="append", default=[])
    args = parser.parse_args()
    if args.verify:
        answer = verify(args.verify.resolve())
    elif args.plan:
        files, external = sources(args.root.resolve(), args.package)
        answer = {"file_count": len(files), "bytes": sum(p.stat().st_size for p in files),
                  "top_levels": sorted({p.relative_to(args.root.resolve()).parts[0] for p in files}),
                  "unbundled_import_roots": external}
    else:
        if not all((args.package, args.output, args.release_id)):
            parser.error("A build requires --package, --output and --release-id")
        if args.source_only and (args.run or args.config):
            parser.error("--source-only cannot include --run or --config")
        if not args.source_only and not (args.run and args.config):
            parser.error("A reference build requires --run and --config; otherwise use --source-only")
        answer = build(args.root.resolve(), args.package,
                       args.run.resolve() if args.run else None, args.config.resolve() if args.config else None,
                       args.output.resolve(), args.release_id, [p.resolve() for p in args.extra],
                       [p.resolve() for p in args.vendor_tree], args.profile.resolve() if args.profile else None)
    print(json.dumps(answer, indent=2))


if __name__ == "__main__":
    main()
