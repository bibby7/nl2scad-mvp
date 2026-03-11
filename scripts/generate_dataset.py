#!/usr/bin/env python3
"""Generate synthetic NL↔OpenSCAD pairs for MVP training.

Usage:
  python scripts/generate_dataset.py --count 3000 --out data/train.jsonl
"""
import argparse
import json
import math
import random
from datetime import datetime

random.seed(42)

TEMPLATES = []

# --- Template: hollow cylinder ---
def hollow_cylinder_sample():
    inner_d = random.choice([4, 5, 6, 8, 10, 12])
    wall = random.choice([1.2, 1.5, 2.0, 2.5])
    height = random.choice([10, 12, 15, 20, 25, 30])
    outer_d = inner_d + 2 * wall
    prompt = (
        f"Create a hollow cylinder for 3D printing. "
        f"Inner diameter {inner_d}mm, wall thickness {wall}mm, height {height}mm. "
        f"Use millimeters and make it watertight." )

    scad = f"""// Hollow cylinder (mm)\n$fn=96;\n\ninner_d = {inner_d};\nwall = {wall};\nouter_d = inner_d + 2*wall;\nheight = {height};\n\nmodule hollow_cylinder() {{\n    difference() {{\n        cylinder(d=outer_d, h=height, center=false);\n        cylinder(d=inner_d, h=height+0.2, center=false);\n    }}\n}}\n\nhollow_cylinder();\n"""
    return prompt, scad

TEMPLATES.append(hollow_cylinder_sample)

# --- Template: box with through-holes ---
def box_with_holes_sample():
    length = random.choice([40, 50, 60, 80])
    width  = random.choice([20, 30, 40])
    height = random.choice([10, 12, 15, 20])
    hole_d = random.choice([3, 4, 5])
    edge_offset = random.choice([6, 8, 10])
    prompt = (
        f"Make a rectangular block {length}x{width}x{height}mm with two through-holes. "
        f"Hole diameter {hole_d}mm, centered along the width, {edge_offset}mm from each end. "
        f"Print flat on the largest face." )

    scad = f"""// Box with through-holes (mm)\n$fn=96;\n\nlength = {length};\nwidth  = {width};\nheight = {height};\nhole_d = {hole_d};\nedge_offset = {edge_offset};\n\nmodule box_with_holes() {{\n    difference() {{\n        cube([length, width, height], center=false);\n        for (x = [edge_offset, length-edge_offset]) {{\n            translate([x, width/2, height/2])\n                rotate([90,0,0])\n                cylinder(d=hole_d, h=width+0.2, center=true);\n        }}\n    }}\n}}\n\nbox_with_holes();\n"""
    return prompt, scad

TEMPLATES.append(box_with_holes_sample)

# --- Template: L-bracket ---
def l_bracket_sample():
    length = random.choice([40, 50, 60])
    width  = random.choice([20, 25, 30])
    thickness = random.choice([3, 4, 5])
    leg_height = random.choice([20, 25, 30])
    hole_d = random.choice([3, 4])
    prompt = (
        f"Create an L-bracket: base {length}x{width}mm, thickness {thickness}mm, "
        f"vertical leg height {leg_height}mm. Add a {hole_d}mm hole centered on each leg." )

    scad = f"""// L-bracket (mm)\n$fn=96;\n\nlength = {length};\nwidth = {width};\nthickness = {thickness};\nleg_height = {leg_height};\nhole_d = {hole_d};\n\nmodule l_bracket() {{\n    difference() {{\n        union() {{\n            cube([length, width, thickness], center=false);\n            translate([0, 0, thickness])\n                cube([thickness, width, leg_height], center=false);\n        }}\n        // base hole
        translate([length/2, width/2, thickness/2])\n            rotate([90,0,0])\n            cylinder(d=hole_d, h=width+0.2, center=true);\n        // vertical leg hole
        translate([thickness/2, width/2, thickness + leg_height/2])\n            rotate([0,90,0])\n            cylinder(d=hole_d, h=thickness+0.2, center=true);\n    }}\n}}\n\nl_bracket();\n"""
    return prompt, scad

TEMPLATES.append(l_bracket_sample)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=3000)
    ap.add_argument("--out", type=str, default="data/train.jsonl")
    args = ap.parse_args()

    out_path = args.out
    with open(out_path, "w", encoding="utf-8") as f:
        for _ in range(args.count):
            fn = random.choice(TEMPLATES)
            prompt, scad = fn()
            obj = {"prompt": prompt, "response": scad}
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {args.count} samples to {out_path}")


if __name__ == "__main__":
    main()
