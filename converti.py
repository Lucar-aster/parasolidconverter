import os
import subprocess
import sys

def converti_tutti_i_file():
    cartella_corrente = os.getcwd()
    file_xt = [f for f in os.listdir(cartella_corrente) if f.lower().endswith(('.x_t', '.x_b'))]
    
    if not file_xt:
        print("❌ Nessun file .x_t o .x_b trovato nella cartella corrente.")
        print("💡 Trascina i tuoi file .x_t nella colonna di sinistra di GitHub e riprova.")
        return

    print(f"📦 Trovati {len(file_xt)} file da convertire...")

    for i, file_in in enumerate(file_xt, 1):
        nome_base = os.path.splitext(file_in)[0]
        file_out = f"{nome_base}.step"
        
        print(f"[{i}/{len(file_xt)}] Convertendo: {file_in} -> {file_out}...")
        
        # Script FreeCAD eseguito internamente
        cmd_freecad = (
            f"import Part; "
            f"shape = Part.Shape(); "
            f"shape.read('{file_in}'); "
            f"shape.exportStep('{file_out}')"
        )
        
        try:
            result = subprocess.run(
                ["freecadcmd", "-c", cmd_freecad],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if os.path.exists(file_out):
                print(f"   ✅ OK: Generato {file_out}")
            else:
                print(f"   ❌ Errore nella conversione di {file_in}")
        except Exception as e:
            print(f"   ❌ Errore inatteso: {e}")

    print("\n🎉 Processo di conversione completato per tutti i file!")

if __name__ == "__main__":
    converti_tutti_i_file()
