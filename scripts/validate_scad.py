#!/usr/bin/env python3
"""Validate OpenSCAD → STL and check mesh watertightness.

Usage:
  python scripts/validate_scad.py --scad model.scad --stl out.stl
"""
import argparse
import subprocess
import sys
import trimesh


def run_openscad(scad_path, stl_path):
    cmd = ["openscad", "-o", stl_path, scad_path]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def check_mesh(stl_path):
    mesh = trimesh.load(stl_path, force="mesh")
    if mesh.is_empty:
        return False, "mesh empty"
    return bool(mesh.is_watertight), f"watertight={mesh.is_watertight}, volume={mesh.volume:.4f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scad", required=True)
    ap.add_argument("--stl", required=True)
    args = ap.parse_args()

    code, out, err = run_openscad(args.scad, args.stl)
    if code != 0:
        print("OpenSCAD failed:", err.strip())
        sys.exit(1)

    ok, msg = check_mesh(args.stl)
    print(msg)
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
