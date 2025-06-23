import pdfplumber, re, json, csv
from pathlib import Path
import sys

# Constants for item codes and their descriptions
DESC = {
    "HHWS": "Heating Hot Water Supply",
    "HHWR": "Heating Hot Water Return",
    "CHWS": "Chilled Water Supply",
    "CHWR": "Chilled Water Return",
    "CWS" : "Condenser Water Supply",
    "CWR" : "Condenser Water Return",
    "HUH" : "Unit Heater (Hot-Water)",
    "FCU" : "Fan-Coil Unit",
    "MAU" : "Make-up Air Unit",
    "HX"  : "Heat Exchanger",
    "AS"  : "Air Separator",
    "BC"  : "Blower Curtain",
    "VAV" : "Variable-Air-Volume Box",
    "CHWP": "Chilled-Water Pump",
    "CWP" : "Condenser-Water Pump",
    "ET"  : "Expansion Tank",
    "B"   : "Boiler",
    "BCP" : "Boiler Circ. Pump",
    "CFS" : "Chem-Feed Storage",
}


ITEM_RE  = re.compile(r'\b(' + "|".join(DESC) + r')\b')
MODEL_RE = re.compile(r'\b([A-Z]{2,5}[-\s]?\d{1,4})\b')
DIM_RE   = re.compile(r"\d+'\s*-\s*\d+\s*\d*/?\d*\"|\d+\"|\d+\s*ø")
BE_RE    = re.compile(r'BE\s*=\s*([\d\'\- ]+[\/\d\"]+)')
MOUNT_STRINGS = ["wall-hung", "floor-mounted", "ceiling-hung", "above ceiling"]


def parse_line(line, page_idx):
    entry = {"page": page_idx + 1}

    # mounting
    for m in MOUNT_STRINGS:
        if m in line.lower(): entry["mounting"] = m; break

    # item code
    m = ITEM_RE.search(line)
    if m: entry["code"] = m.group(1)

    # model-/detail-number
    mm = MODEL_RE.search(line)
    if mm: entry["model"] = mm.group(1).replace(" ", "")

    # pipe length (BE = …)
    be = BE_RE.search(line)
    if be: entry["run_len"] = be.group(1).strip()

    # one representative dimension (first quoted number or ø-size)
    dims = DIM_RE.findall(line)
    if dims:
        # pick first dimension that looks like diameter (ends with " or ø)
        for d in dims:
            if "\"" in d or "ø" in d:
                entry["size"] = d.strip()
                break
        # keep the rest as free-text notes if interesting
        if len(dims) > 1:
            entry["extra_dims"] = "; ".join(dims[1:]).strip()

    return entry if any(k in entry for k in ("code", "model")) else None
 
def extract(pdf_path: str, start_page=None, end_page=None):
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        s = start_page-1 if start_page else 0
        e = end_page if end_page else total_pages
        for i in range(s, e):
            page = pdf.pages[i]
            print(f"• page {i+1}/{total_pages}")
            text = page.extract_text() or ""
            for ln in text.splitlines():
                r = parse_line(ln, i)
                if r: rows.append(r)
    return rows

 
def tidy(rows):
    cleaned = []
    for r in rows:
        # drop lone boiler/AS rows with nothing else
        if r.get("code") in {"B", "AS"} and len(r) == 2:
            continue

        if "code" in r:
            r["description"] = DESC.get(r["code"], r["code"])

        cleaned.append(r)
    return cleaned
 
def save_json(rows, fn="processed_data.json"):
    Path(fn).write_text(json.dumps(rows, indent=2))

def json_to_csv(json_file, csv_file):
    data = json.loads(Path(json_file).read_text())

    headers = set()
    for row in data:
        headers.update(row.keys())

    with open(csv_file, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(headers))
        writer.writeheader()
        writer.writerows(data)

def process_row(row):
    processed_row = {
        "Item/Fixture Type": str(row.get("description", "")).strip(),
        "Quantity": str(row.get("run_len", "")).strip(),
        "Model Number / Spec Reference": str(row.get("code", "")).strip(),
        "Page Reference": str(row.get("page", "")).strip(),
        "Associated Dimensions": str(row.get("extra_dims", "")).strip(),
        "Mounting Type": str(row.get("mounting", "")).strip(),
    }
    # Remove rows where only 'Page Reference' is non-empty
    non_page_fields = [k for k in processed_row if k != "Page Reference"]
    if all(processed_row[k] == "" for k in non_page_fields) and processed_row["Page Reference"] != "":
        return None
    
    # Filter out rows with no meaningful data
    if all(value == "" for value in processed_row.values()):
        return None
    return processed_row

def process_data(extracted_data):
    processed_data = []
    for row in extracted_data:
        processed_row = process_row(row)
        if processed_row:
            processed_data.append(processed_row)
    return processed_data

if __name__ == "__main__":
    PDF = "M&P mark-up against shop systems piping.pdf" 
    args = sys.argv[1:]
    if len(args) == 2:
        start_page, end_page = int(args[0]), int(args[1])
    elif len(args) == 1:
        start_page = int(args[0])
        end_page = start_page
    else:
        start_page = 1
        end_page = 2
    extracted_data = tidy(extract(PDF, start_page, end_page))
    # output_json = "extracted_data.json"
    # save_json(extracted_data, output_json)
    # json_to_csv("extracted_data.json", "extracted_data.csv")
 
    processed_data = process_data(extracted_data)
    Path("processed_data.json").write_text(json.dumps(processed_data, indent=2))
    json_to_csv("processed_data.json", "processed_data.csv")
