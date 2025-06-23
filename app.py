import streamlit as st
import pandas as pd
import tempfile
from main import extract, tidy, process_data
import pdfplumber

st.title("Construction Intelligence App")

log_area = st.empty()

uploaded_file = st.file_uploader("Upload a Construction PDF file", type=["pdf"])
if uploaded_file:
    log_area.info("PDF uploaded. Preparing to process...")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name
    with pdfplumber.open(tmp_file_path) as pdf:
        total_pages = len(pdf.pages)
    st.write(f"PDF has {total_pages} pages.")
    start_page = st.number_input("Start Page", min_value=1, max_value=total_pages, value=1)
    end_page = st.number_input("End Page", min_value=1, max_value=total_pages, value=total_pages)
    if st.button("Extract Data"):
        log_area.info(f"Extracting data from page {start_page} to {end_page}...")
        raw_data = extract(tmp_file_path, start_page, end_page)
        cleaned_data = tidy(raw_data)
        processed_data = process_data(cleaned_data)
        log_area.success(f"Extraction complete. {len(processed_data)} rows extracted.")
        st.dataframe(pd.DataFrame(processed_data), use_container_width=True)
else:
    st.info("Please upload a PDF file to begin.")