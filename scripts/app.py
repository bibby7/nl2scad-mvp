#!/usr/bin/env python3
import subprocess
from pathlib import Path
import gradio as gr

BASE_MODEL = "mlx-community/Qwen2.5-7B-Instruct"
LORA_PATH = "./lora-openscad"
TEMPLATE = Path("./prompt_template.txt").read_text()


def generate_scad(user_prompt):
    full_prompt = TEMPLATE.replace("{USER_PROMPT}", user_prompt)
    cmd = [
        "mlx_lm.generate",
        "--model", BASE_MODEL,
        "--lora", LORA_PATH,
        "--prompt", full_prompt,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return f"ERROR: {proc.stderr}"
    return proc.stdout


def validate(scad_text):
    outdir = Path("./out")
    outdir.mkdir(parents=True, exist_ok=True)
    scad_path = outdir / "model.scad"
    stl_path = outdir / "model.stl"
    scad_path.write_text(scad_text)

    cmd = ["python", "scripts/validate_scad.py", "--scad", str(scad_path), "--stl", str(stl_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return f"Invalid STL: {proc.stdout} {proc.stderr}", None
    return proc.stdout.strip(), str(stl_path)


with gr.Blocks() as demo:
    gr.Markdown("# NL → OpenSCAD MVP")
    prompt = gr.Textbox(label="Prompt", lines=4, placeholder="Describe the part with measurements...")
    scad = gr.Code(label="OpenSCAD", language="scad")
    status = gr.Textbox(label="Validation")
    stl = gr.File(label="STL Output")

    gen_btn = gr.Button("Generate")
    val_btn = gr.Button("Validate")

    gen_btn.click(fn=generate_scad, inputs=prompt, outputs=scad)
    val_btn.click(fn=validate, inputs=scad, outputs=[status, stl])


demo.launch()
