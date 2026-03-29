import pandas as pd
from pathlib import Path
import subprocess
import tempfile
import shutil
import sys
import re
import os

CSV_FILE = "products.csv"
TEX_TEMPLATE = "label-template.tex"

# Create output directories if they don't exist
TEX_DIR = Path("generated-tex")
PDF_DIR = Path("generated-pdf")
TEX_DIR.mkdir(exist_ok=True)
PDF_DIR.mkdir(exist_ok=True)

EU_ALLERGENS = {
    'gluten', 'wheat', 'rye', 'barley', 'oats', 'crustaceans', 'crabs', 'prawns', 'lobsters',
    'eggs', 'egg', 'fish', 'peanuts', 'soya', 'soy', 'soybeans', 'milk', 'nuts', 'almonds',
    'hazelnuts', 'walnuts', 'cashews', 'pecan', 'brazil nuts', 'pistachio', 'macadamia',
    'celery', 'mustard', 'sesame', 'sulphur dioxide', 'sulphites', 'sulfites', 'lupin',
    'molluscs', 'mussels', 'oysters', 'squid', 'snails', 'lecithins'
}

def latex_escape_ingredients(text: str) -> str:
    """Escape ingredients AFTER bold markers, escape % FIRST to prevent truncation."""
    text = str(text)
    text = text.replace('%', r'\%')
    text = text.replace('&', r'\&')
    return text

def highlight_allergens(ingredients: str) -> str:
    """Wrap EU allergens in \textbf{}."""
    text = str(ingredients)
    print(f"🔍 Original: {text[:100]}...")
    
    for allergen in EU_ALLERGENS:
        pattern = r'\b' + re.escape(allergen) + r'\b'
        def bold_match(match):
            return r'\textbf{' + match.group(0) + '}'
        text = re.sub(pattern, bold_match, text, flags=re.IGNORECASE)
    
    print(f"🔍 Bolded:   {text[:100]}...")
    return text

def process_ingredients(ingredients_raw: str) -> str:
    """Highlight allergens → escape ingredients properly."""
    ingredients_marked = highlight_allergens(ingredients_raw)
    ingredients_tex = latex_escape_ingredients(ingredients_marked)
    print(f"🔍 TEX:     {ingredients_tex[:150]}...")
    print("-" * 80)
    return ingredients_tex

def latex_escape_plain(text: str) -> str:
    """Escape for non-ingredients."""
    if pd.isna(text):
        return ""
    text = str(text)
    replacements = {
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
        "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\hat{}",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def get_nutrition_table(row):
    if not bool(row.get("nutritional_information", False)):
        return ""
    def val(col): return latex_escape_plain(str(row.get(col, "")))
    return f"""\\begin{{tabular}}{{@{{}}l r@{{}}}}
\\multicolumn{{2}}{{@{{}}l@{{}}}}{{\\textbf{{Nutritional Values}} \\hfill (per 100g)}} \\\\ \\hline
\\textbf{{Energy}} & {val('energy_kj')} / {val('energy_kcal')} \\\\
\\textbf{{Fat}} & {val('fat_total')} \\\\
\\quad of which saturates & {val('fat_saturates')} \\\\
\\textbf{{Carbohydrate}} & {val('carbohydrates')} \\\\
\\quad of which sugars & {val('sugars')} \\\\
\\textbf{{Fiber}} & {val('fibre')} \\\\
\\textbf{{Protein}} & {val('protein')} \\\\
\\textbf{{Salt}} & {val('salt')} \\\\
\\end{{tabular}}"""

def process_row(row, index):
    """Process a single row and generate TEX/PDF files."""
    print(f"\n📦 Processing row {index + 1}: {row.get('product_name', 'Unnamed')}")
    
    # Process ingredients FIRST
    ingredients_tex = process_ingredients(row["list_of_ingredients"])
    
    template_text = Path(TEX_TEMPLATE).read_text(encoding="utf-8")
    
    placeholders = {
        "{PRODUCT_NAME}": latex_escape_plain(str(row["product_name"])),
        "{LIST_OF_INGREDIENTS}": ingredients_tex,
        "{BARCODE_NUMBER}": latex_escape_plain(str(row["barcode_number"])),
        "{NET_QUANTITY}": latex_escape_plain(str(row["net_quantity"])),
        "{E_MARK}": latex_escape_plain(str(row["e_mark"])),
        "{DRAINED_WEIGHT}": latex_escape_plain(str(row["drained_weight"])),
        "{BRAND_LOGO}": latex_escape_plain(str(row["brand_logo"])),
        "{BUSINESS_ADDRESS}": latex_escape_plain(str(row["business_address"])),
        "{BEST_BEFORE_DATE}": latex_escape_plain(str(row["best_before_date"])),
    }
    
    final_tex = template_text
    for ph, val in placeholders.items():
        final_tex = final_tex.replace(ph, val)
    
    # Nutrition table replacement
    nutrition_table = get_nutrition_table(row)
    block = r"""\begin{tabular}{@{}l r@{}}
\multicolumn{2}{@{}l@{}}{\textbf{Nutritional Values} \hfill (per 100g)} \\ \hline
\textbf{Energy} & {ENERGY_KJ} / {ENERGY_KCAL} \\
\textbf{Fat} & {FAT_TOTAL} \\
\quad of which saturates & {FAT_SATURATES} \\
\textbf{Carbohydrate} & {CARBOHYDRATES} \\
\quad of which sugars & {SUGARS} \\
\textbf{Fiber} & {FIBRE} \\
\textbf{Protein} & {PROTEIN} \\
\textbf{Salt} & {SALT} \\
\end{tabular}"""
    if nutrition_table:
        final_tex = final_tex.replace(block, nutrition_table)
    else:
        start = r"""\begin{tikzpicture}
\node[draw,rounded corners=4pt,line width=0.4pt,inner sep=4pt,outer sep=0pt,anchor=north west] (box) at (0,0) {%"""
        end = r"""\end{tikzpicture}"""
        i = final_tex.find(start)
        if i != -1:
            j = final_tex.find(end, i) + len(end)
            final_tex = final_tex[:i] + final_tex[j:]
    
    # Generate safe filename from product name
    safe_name = re.sub(r'[^\w\-_\.]', '_', str(row["product_name"]))[:50]
    tex_filename = f"label_{index+1:03d}_{safe_name}.tex"
    pdf_filename = f"label_{index+1:03d}_{safe_name}.pdf"
    
    tex_path = TEX_DIR / tex_filename
    pdf_path = PDF_DIR / pdf_filename
    
    # Save TEX file
    tex_path.write_text(final_tex, encoding="utf-8")
    print(f"✅ Wrote {tex_path}")
    
    # Generate PDF
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            tmp_tex = tmp_path / tex_filename
            tmp_pdf = tmp_path / pdf_filename
            
            tmp_tex.write_text(final_tex, encoding="utf-8")
            
            for _ in range(2):
                subprocess.run([
                    "pdflatex", "-interaction=nonstopmode", 
                    "-output-directory", str(tmp_path), 
                    str(tmp_tex)
                ], check=True, capture_output=True)
            
            shutil.copy2(tmp_pdf, pdf_path)
        print(f"✅ Created {pdf_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ pdflatex error for row {index+1}: {e}")
    except Exception as e:
        print(f"❌ Error processing row {index+1}: {e}")

def main():
    """Process all rows in CSV."""
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"📊 Found {len(df)} products to process")
        
        for index, row in df.iterrows():
            process_row(row, index)
        
        print(f"\n🎉 Completed! Check folders:")
        print(f"   📁 TEX:  {TEX_DIR.absolute()}")
        print(f"   📁 PDF:  {PDF_DIR.absolute()}")
        print(f"   📄 {len(list(TEX_DIR.glob('*.tex')))} TEX files generated")
        print(f"   📄 {len(list(PDF_DIR.glob('*.pdf')))} PDF files generated")
        
    except FileNotFoundError:
        print(f"❌ CSV file '{CSV_FILE}' not found!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Main error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()