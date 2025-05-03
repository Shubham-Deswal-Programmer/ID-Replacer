import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io
import os

def replace_text_in_pdf(pdf_bytes, replacements):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        for old, new in replacements.items():
            text_instances = page.search_for(old)
            for inst in text_instances:
                page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()
            for inst in text_instances:
                # Apply 4-pixel vertical correction
                new_position = fitz.Point(inst.tl.x, inst.tl.y + 8)
                page.insert_text(new_position, new, fontsize=12, color=(0, 0, 0))
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    return output

st.title("PDF ID to Name Replacer")

st.markdown("""
Upload a **PDF** file and a **CSV** file containing ID-to-name mappings.  
The CSV should have two columns: first for ID, second for the replacement name.  
No header is required.
""")

pdf_file = st.file_uploader("Upload PDF", type="pdf")
csv_file = st.file_uploader("Upload CSV (ID,Name)", type="csv")

if pdf_file and csv_file:
    try:
        df = pd.read_csv(csv_file, header=None)
        replacements = dict(zip(df[0], df[1]))

        if st.button("Replace IDs with Names"):
            result_pdf = replace_text_in_pdf(pdf_file.read(), replacements)

            original_filename = os.path.splitext(pdf_file.name)[0]
            new_filename = f"{original_filename}_updated.pdf"

            st.success("PDF processed successfully!")
            st.download_button(
                label="Download Updated PDF",
                data=result_pdf,
                file_name=new_filename,
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Error: {e}")
