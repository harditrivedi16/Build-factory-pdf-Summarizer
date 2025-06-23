# README
# Build Factory --> PDF Summarizer

## Overview
This project processes construction-related data extracted from a PDF file and generates structured JSON and csv files (`processed_data.json` and `processed_data.csv`).

I have not used LLMs here, instead used `pdfplumber` library and parsing logic (plus regular expressions) to extract information directly from the PDF.

## Assumptions
1. **Abbreviations**:
   The script uses predefined abbreviations mapped to full descriptions. For example:
   - `HHWS`: Heating Hot Water Supply
   - `HHWR`: Heating Hot Water Return
   - `CHWS`: Chilled Water Supply
   - `CHWR`: Chilled Water Return
   - `CWS`: Condenser Water Supply
   - `CWR`: Condenser Water Return
   - `HUH`: Unit Heater (Hot-Water)
   - `FCU`: Fan-Coil Unit
   - `MAU`: Make-up Air Unit
   - `HX`: Heat Exchanger
   - `AS`: Air Separator
   - `BC`: Blower Curtain
   - `VAV`: Variable-Air-Volume Box
   - `CHWP`: Chilled-Water Pump
   - `CWP`: Condenser-Water Pump
   - `ET`: Expansion Tank
   - `B`: Boiler
   - `BCP`: Boiler Circ. Pump
   - `CFS`: Chem-Feed Storage

2. **Pattern Helpers**:
   The script uses regular expressions to identify:
   - **Item codes**: Matches predefined abbreviations like `HHWS`, `CHWS`, `CWS`, etc.
   - **Model numbers**: Matches patterns like `BC1`, `MAU-11`, `HX-142`, etc.
   - **Dimensions**: Matches patterns like `2' - 6"`, `6"`, `1' - 9"`, etc.
   - **Mounting types**: Identifies strings like `wall-hung`, `floor-mounted`, `ceiling-hung`, `above ceiling`.

 

## Steps to Run
1. **Install Dependencies**:
   Install the required libraries using:
   ```bash
   pip install -r requirements.txt
   ```

2. **Place the PDF**:
   Place the input PDF file in the same directory as the script.

3. **Run the Python Script**:
   Execute the script using, (default: pages 1-2):
   ```bash
   python main.py
   ```
   How to run for a specific page or range:
   ```bash
   python main.py 3 5
   ```

4. **Run the UI App**:
   Launch the Streamlit app `Construction Intelligence App` using:
   ```bash
   streamlit run app.py
   ```

## Output
- The processed data will be saved in `processed_data.json` and `processed_data.csv`.
- The Streamlit app provides a user-friendly interface to view the data.
