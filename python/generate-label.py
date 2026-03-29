import pandas as pd
from pathlib import Path
import subprocess
import tempfile
import shutil
import sys
import os

CSV_FILE = "product.csv"
TEX_TEMPLATE = "label-template.tex"  # Renamed from label-2.tex
OUTPUT_TEX = "label-output.tex"
OUTPUT_PDF = "label-output.pdf"

def latex_escape(text):
    """Escape special LaTeX characters."""
    if pd.isna(text):
        return ""
    text = str(text)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def cleanup_aux_files(path):
    """Remove LaTeX auxiliary files."""
    for ext in ['.aux', '.log', '.synctex.gz', '.synctex(busy)']:
        aux_file = path.with_suffix('') / (path.stem + ext)
        if aux_file.exists():
            aux_file.unlink()
            print(f"🧹 Cleaned {aux_file.name}")

def main():
    # Read CSV data
    df = pd.read_csv(CSV_FILE)
    row = df.iloc[0]  # Use first row
    
    # Read template
    template_text = Path(TEX_TEMPLATE).read_text(encoding="utf-8")
    
    # Define all placeholders and their CSV mappings
    placeholders = {
        "{PRODUCT_NAME}": latex_escape(row["product_name"]),
        "{LIST_OF_INGREDIENTS}": latex_escape(row["list_of_ingredients"]),
        "{BARCODE_NUMBER}": latex_escape(row["barcode_number"]),
        "{NET_QUANTITY}": latex_escape(row["net_quantity"]),
        "{BRAND_LOGO}": latex_escape(row["brand_logo"]),
        "{BUSINESS_ADDRESS}": latex_escape(row["business_address"]),
        "{BEST_BEFORE_DATE}": latex_escape(row["best_before_date"]),
        "{ENERGY_KJ}": latex_escape(row["energy_kj"]),
        "{ENERGY_KCAL}": latex_escape(row["energy_kcal"]),
        "{FAT_TOTAL}": latex_escape(row["fat_total"]),
        "{FAT_SATURATES}": latex_escape(row["fat_saturates"]),
        "{CARBOHYDRATES}": latex_escape(row["carbohydrates"]),
        "{SUGARS}": latex_escape(row["sugars"]),
        "{FIBRE}": latex_escape(row["fibre"]),
        "{PROTEIN}": latex_escape(row["protein"]),
        "{SALT}": latex_escape(row["salt"]),
    }
    
    # Replace placeholders in template
    final_tex = template_text
    for placeholder, value in placeholders.items():
        final_tex = final_tex.replace(placeholder, value)
    
    # Write output TEX file
    Path(OUTPUT_TEX).write_text(final_tex, encoding="utf-8")
    print(f"✅ Created {OUTPUT_TEX} with CSV data")
    
    # Compile to PDF using pdflatex
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Copy output tex to temp dir
            tex_temp = tmp_path / OUTPUT_TEX
            tex_temp.write_text(final_tex, encoding="utf-8")
            
            # Run pdflatex twice (for references/tables)
            for i in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(tmp_path), str(tex_temp)],
                    capture_output=True,
                    text=True,
                    check=True
                )
            
            # Copy PDF to output
            pdf_temp = tmp_path / OUTPUT_PDF
            shutil.copy2(pdf_temp, OUTPUT_PDF)
        
        # Clean up any aux files that might have escaped to working directory
        cleanup_aux_files(Path(OUTPUT_TEX))
        cleanup_aux_files(Path(OUTPUT_PDF))
        
        print(f"✅ Created {OUTPUT_PDF}")
        print("🧹 All auxiliary files cleaned up!")
        print("📄 Files generated successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ pdflatex failed:")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("❌ pdflatex not found. Install TeX Live or MiKTeX.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()