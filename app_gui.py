import streamlit as st
import os
import subprocess

st.set_page_config(page_title="Convertitore CAD .x_t a STEP", layout="centered")

st.title("⚙️ Convertitore Parasolid (.x_t) in STEP (.step)")
st.write("Carica i tuoi file CAD qui sotto, convertili in blocco e scaricali con un clic.")

# Area per caricare i file (supporta la selezione multipla)
uploaded_files = st.file_uploader(
    "Seleziona o trascina i file .x_t o .x_b", 
    type=["x_t", "x_b", "X_T", "X_B"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📁 Caricati {len(uploaded_files)} file. Pronto per la conversione.")
    
    if st.button("🚀 Avvia Conversione in Massa", type="primary"):
        barra_progresso = st.progress(0)
        totale = len(uploaded_files)
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Salva temporaneamente il file caricato nel Codespace
            input_name = uploaded_file.name
            with open(input_name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            output_name = os.path.splitext(input_name)[0] + ".step"
            
            # Comando FreeCAD per la conversione
            cmd_freecad = (
                f"import Part; "
                f"shape = Part.Shape(); "
                f"shape.read('{input_name}'); "
                f"shape.exportStep('{output_name}')"
            )
            
            # Esegue la conversione
            subprocess.run(["freecadcmd", "-c", cmd_freecad], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Mostra il risultato e crea il pulsante di download per ogni singolo file
            if os.path.exists(output_name):
                st.success(f"✅ {input_name} -> {output_name} convertito con successo!")
                with open(output_name, "rb") as f_down:
                    st.download_button(
                        label=f"📥 Scarica {output_name}",
                        data=f_down,
                        file_name=output_name,
                        mime="application/octet-stream",
                        key=f"dl_{i}"
                    )
            else:
                st.error(f"❌ Errore durante la conversione di {input_name}")
                
            # Aggiorna la barra di progresso
            barra_progresso.progress((i + 1) / totale)
            
        st.balloons()
        st.success("🎉 Tutti i file elaborati!")
