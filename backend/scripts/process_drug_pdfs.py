import camelot
import pandas as pd
import os
import sys
import glob

# Set encoding to avoid issues on Windows
sys.stdout.reconfigure(encoding="utf-8")

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: Since this script is in backend/scripts, we go up one level to reach backend/
BACKEND_DIR = os.path.dirname(BASE_DIR)
PDF_DIR = os.path.join(BACKEND_DIR, "data")
CSV_DIR = os.path.join(BACKEND_DIR, "data", "csv")


def setup_environment():
    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR, exist_ok=True)
        print(f" Created directory: {CSV_DIR}")


def convert_pdf(pdf_path):
    pdf_name = os.path.basename(pdf_path)
    output_csv_name = pdf_name.replace(".pdf", ".csv").replace(" ", "_").lower()
    output_path = os.path.join(CSV_DIR, output_csv_name)

    print(f"\n Processing: {pdf_name}...")

    try:
        # Lattice mode is usually better for tables with borders
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")

        # If lattice finds nothing, try stream (for tables without borders)
        if len(tables) == 0:
            print(f"ℹ Lattice found no tables, trying stream mode...")
            tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")

        if len(tables) == 0:
            print(f"⚠️ No tables found in {pdf_name}")
            return None

        df_list = []
        for table in tables:
            df_list.append(table.df)

        final_df = pd.concat(df_list, ignore_index=True)
        final_df.to_csv(output_path, index=False)
        print(f" Converted to raw CSV: {output_csv_name}")
        return output_path
    except Exception as e:
        print(f" Error converting {pdf_name}: {e}")
        return None


def clean_csv(csv_path):
    if not csv_path or not os.path.exists(csv_path):
        return

    csv_name = os.path.basename(csv_path)
    cleaned_name = f"cleaned_{csv_name}"
    cleaned_path = os.path.join(CSV_DIR, cleaned_name)

    print(f" Cleaning: {csv_name}...")
    try:
        df = pd.read_csv(csv_path)

        # Initial cleanup: Remove empty rows or columns
        df = df.dropna(how="all").dropna(axis=1, how="all")

        # If columns are just numbers 0, 1, 2... try to promote first row to header
        if all(str(c).isdigit() for c in df.columns[:2]) and not df.empty:
            header = df.iloc[0]
            df = df[1:]
            df.columns = header

        # Normalize column names
        df.columns = [
            str(c).lower().strip().replace(" ", "_").replace("\n", "_").replace(".", "")
            for c in df.columns
        ]

        # Standardize column names for the seeder
        rename_map = {
            "drugs_name": "salt",
            "drug_name": "salt",
            "composition": "salt",
            "name_of_the_fdc": "salt",
            "composition_of_the_fdc": "salt",
            "brand_name": "brand",
            "notification_no__&_date": "notification",
            "notification_no_&_date": "notification",
            "notification_no_&_date": "notification",
        }

        df = df.rename(columns=rename_map)

        # For the "Prohibited FDC 156" list, it has a specific column for brand/name
        if "156" in csv_name:
            # Just ensures we don't lose anything
            pass

        df.to_csv(cleaned_path, index=False)
        print(f" Saved cleaned CSV: {cleaned_name}")
        return cleaned_path
    except Exception as e:
        print(f" Error cleaning {csv_name}: {e}")
        return None


if __name__ == "__main__":
    setup_environment()

    # Get all PDFs in the data directory
    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    print(f" Found {len(pdf_files)} PDF files in {PDF_DIR}")

    for pdf in pdf_files:
        raw_csv = convert_pdf(pdf)
        if raw_csv:
            clean_csv(raw_csv)

    print("\n🎉 All 8 PDFs processed!")
