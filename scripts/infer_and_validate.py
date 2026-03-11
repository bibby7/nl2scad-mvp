#!/usr/bin/env python3
"""Generate OpenSCAD from prompt (MLX) and validate STL.

Usage:
  python scripts/infer_and_validate.py "your prompt here"
"""
import argparse
import subprocess
import os
from pathlib import Path


def load_template(path):
    return Path(path).read_text()


def run_mlx(prompt, model="mlx-community/Qwen2.5-7B-Instruct", lora="./lora-openscad"):
    cmd = [
        "mlx_lm.generate",
        "--model", model,
        "--lora", lora,
        "--prompt", prompt,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--model", default="mlx-community/Qwen2.5-7B-Instruct")
    ap.add_argument("--lora", default="./lora-openscad")
    ap.add_argument("--outdir", default="./out")
    ap.add_argument("--template", default="./prompt_template.txt")
    ap.add_argument("--retries", type=int, default=2)
    args = ap.parse_args()

    Path(args.outdir).mkdir(parents=True, exist_ok=True)

    template = load_template(args.template)

    last_err = None
    for attempt in range(args.retries + 1):
        full_prompt = template.replace("{USER_PROMPT}", args.prompt)
        scad_text = run_mlx(full_prompt, args.model, args.lora)

        scad_path = Path(args.outdir) / "model.scad"
        scad_path.write_text(scad_text)

        stl_path = Path(args.outdir) / "model.stl"
        cmd = ["python", "scripts/validate_scad.py", "--scad", str(scad_path), "--stl", str(stl_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        print(proc.stdout.strip())
        if proc.returncode == 0:
            return
        last_err = proc.stderr.strip()

    if last_err:
        print(last_err)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
