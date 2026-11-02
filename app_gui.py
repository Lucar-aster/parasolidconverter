import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Parasolid .x_t / .x_b -> STEP",
    page_icon="📦",
    layout="centered",
)

st.title("📦 Convertitore Parasolid (.x_t / .x_b) -> STEP")
st.caption("Converte file CAD Parasolid in formato STEP usando FreeCAD sul backend.")

# --------------------------------------------------------------------
# Utility
# --------------------------------------------------------------------

def find_freecad_cmd():
    candidates = [
        "freecadcmd",
        "/usr/bin/freecadcmd",
        "/usr/local/bin/freecadcmd",
        "/opt/FreeCAD/bin/freecadcmd",
    ]

    for cmd in candidates:
        if shutil.which(cmd):
            return cmd
    return None


def convert_xt_to_step(input_file: Path, output_dir: Path):
    """
    Converte un file .x_t o .x_b in STEP usando FreeCAD.
    """
    freecad_cmd = find_freecad_cmd()
    if not freecad_cmd:
        return False, (
            "FreeCAD non trovato. "
            "Installa `freecadcmd` nel sistema e assicurati che sia nel PATH."
        )

    output_file = output_dir / f"{input_file.stem}.step"

    # Script Python eseguito da FreeCAD
    freecad_script = (
        "import Part; "
        "shape = Part.Shape(); "
        f"shape.read(r'{str(input_file)}'); "
        f"shape.exportStep(r'{str(output_file)}');"
    )

    try:
        result = subprocess.run(
            [freecad_cmd, "-c", freecad_script],
            capture_output=True,
            text=True,
            timeout=180,
        )

        if result.returncode == 0 and output_file.exists():
            return True, str(output_file)

        error_text = result.stderr.strip() or result.stdout.strip() or "Conversione fallita senza messaggio di errore."
        return False, error_text

    except subprocess.TimeoutExpired:
        return False, "Timeout durante la conversione. Il file potrebbe essere molto grande o invalido."
    except Exception as e:
        return False, f"Errore inatteso: {str(e)}"


# --------------------------------------------------------------------
# UI
# --------------------------------------------------------------------

uploaded_files = st.file_uploader(
    "Seleziona uno o più file .x_t / .x_b",
    type=["x_t", "x_b", "X_T", "X_B"],
    accept_multiple_files=True,
)

if not uploaded_files:
    st.info("Carica un file Parasolid (.x_t o .x_b) per iniziare la conversione.")
    st.markdown("""
    ### Requisiti
    - FreeCAD installato con `freecadcmd`
    - File in formato Parasolid testuale (.x_t / .x_b)
    - L’applicazione deve essere eseguita su un ambiente con FreeCAD disponibile
    """)
    st.stop()

st.success(f"📁 Caricati {len(uploaded_files)} file.")

results = []

for uploaded_file in uploaded_files:
    st.markdown("---")
    st.subheader(f"🔍 {uploaded_file.name}")

    # Legge il file in memoria
    file_bytes = uploaded_file.getvalue()

    # Crea una cartella temporanea per il lavoro
    temp_dir = Path(tempfile.mkdtemp(prefix="parasolid_convert_"))
    input_path = temp_dir / uploaded_file.name
    input_path.write_bytes(file_bytes)

    with st.spinner(f"Conversione di {uploaded_file.name} in corso..."):
        ok, message = convert_xt_to_step(input_path, temp_dir)

    if ok:
        output_path = Path(message)
        st.success(f"✅ Conversione completata: {output_path.name}")
        st.write(f"File generato: `{output_path.name}`")

        with open(output_path, "rb") as f:
            st.download_button(
                label=f"⬇️ Scarica {output_path.name}",
                data=f.read(),
                file_name=output_path.name,
                mime="application/octet-stream",
            )

    else:
        st.error(f"❌ Conversione fallita: {message}")

    results.append((uploaded_file.name, ok, message))

st.markdown("---")
st.subheader("📋 Risultati")
for nome, ok, msg in results:
    if ok:
        st.write(f"- {nome}: conversione riuscita")
    else:
        st.write(f"- {nome}: errore - {msg}")
