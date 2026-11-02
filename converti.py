import os
import subprocess
import sys
from pathlib import Path

def find_files(folder):
    return sorted(
        p for p in Path(folder).iterdir()
        if p.is_file() and p.suffix.lower() in {".x_t", ".x_b"}
    )

def convert_file(input_path: Path, output_dir: Path):
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{input_path.stem}.step"

    freecad_script = (
        "import Part; "
        "import sys; "
        f"shape = Part.Shape(); "
        f"shape.read(r'{str(input_path)}'); "
        f"shape.exportStep(r'{str(output_file)}');"
    )

    try:
        result = subprocess.run(
            ["freecadcmd", "-c", freecad_script],
            capture_output=True,
            text=True,
            timeout=180
        )
        if result.returncode == 0 and output_file.exists():
            return True, str(output_file)
        return False, (result.stderr or result.stdout or "Conversione fallita")
    except FileNotFoundError:
        return False, "FreeCAD non trovato: installa freecadcmd"
    except subprocess.TimeoutExpired:
        return False, "Timeout conversione"

def main():
    folder = Path(".").resolve()
    files = find_files(folder)

    if not files:
        print("Nessun file .x_t o .x_b trovato.")
        return

    out_dir = folder / "output"
    out_dir.mkdir(exist_ok=True)

    for file in files:
        ok, msg = convert_file(file, out_dir)
        if ok:
            print(f"OK: {file.name} -> {out_dir / (file.stem + '.step')}")
        else:
            print(f"ERRORE: {file.name} -> {msg}")

if __name__ == "__main__":
    main()
