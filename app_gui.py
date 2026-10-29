import streamlit as st
import re
import os

st.set_page_config(page_title="Parser Parasolid .x_t in Puro Python", layout="centered")

st.title("📄 Analizzatore e Parser Parasolid (.x_t) in Puro Python")
st.write("Questa applicazione elabora i file `.x_t` (file di testo strutturati) direttamente in Python puro, senza dipendenze esterne di sistema, ed è compatibile al 100% con Streamlit Cloud.")

# Area per caricare i file (supporta la selezione multipla)
uploaded_files = st.file_uploader(
    "Seleziona o trascina i file .x_t o .x_b", 
    type=["x_t", "x_b", "X_T", "X_B"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📁 Caricati {len(uploaded_files)} file. Avvio dell'analisi testuale...")
    
    for uploaded_file in uploaded_files:
        st.markdown("---")
        st.subheader(f"🔍 File: {uploaded_file.name}")
        
        # Lettura del file come testo (i file .x_t sono codificati in formato ASCII/testuale)
        try:
            content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        except Exception:
            content = uploaded_file.getvalue().decode("latin-1", errors="ignore")
        
        # Estrazione dell'intestazione tipica dei file Parasolid (header con metadati e versioni)[cite: 1]
        header_section = content.split("**END_OF_HEADER")[0] if "**END_OF_HEADER" in content else content[:1500]
        
        with st.expander("📋 Visualizza Intestazione e Metadati del file"):
            st.text_area("Header Parasolid", header_section, height=200, key=f"header_{uploaded_file.name}")
        
        # Analisi delle caratteristiche del file basata su puro Python
        num_lines = len(content.splitlines())
        has_mesh = "mesh" in content.lower() or "polyline" in content.lower()
        has_lattice = "lattice" in content.lower()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Righe di testo", f"{num_lines:,}")
        with col2:
            st.metric("Presenza Mesh", "Sì" if has_mesh else "No")
        with col3:
            st.metric("Struttura Reticolare", "Sì" if has_lattice else "No")
            
        # Pulsante per estrarre informazioni avanzate o sezioni specifiche
        if st.button(f"Estrai struttura dettagliata da {uploaded_file.name}", key=f"btn_{uploaded_file.name}"):
            with st.spinner("Analisi sintattica in corso..."):
                # Ricerca di sezioni e parti all'interno del file di testo
                parts_found = re.findall(r"\*\*PART\d+;", content)
                
                st.write("**Parti identificate nel file:**", parts_found if parts_found else "Nessuna sezione PART standard trovata")
                
                # Mostra una porzione del corpo del file
                st.markdown("##### Anteprima del contenuto interno:")
                st.code(content[0:1500] + "\n[... Testo troncato per leggibilità ...]", language="text")
                
                # Generazione di un report testuale scaricabile riassuntivo
                report_text = f"--- REPORT ANALISI PARASOLID ---\nNome File: {uploaded_file.name}\nLinee totali: {num_lines}\nHeader:\n{header_section}"
                
                st.download_button(
                    label=f"📥 Scarica Report di Analisi ({uploaded_file.name})",
                    data=report_text,
                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}_report.txt",
                    mime="text/plain",
                    key=f"dl_{uploaded_file.name}"
                )
