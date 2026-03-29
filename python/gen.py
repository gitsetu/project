import pandas as pd
from pathlib import Path
import subprocess
import tempfile
import shutil
import sys
import re

CSVFILE = 'product.csv'
TEXTEMPLATE = 'label-template.tex'
OUTPUTTEX = 'label-output.tex'
OUTPUTPDF = 'label-output.pdf'

EU_ALLERGENS = [
    'gluten', 'wheat', 'rye', 'barley', 'oats', 'crustaceans', 'crabs', 'prawns', 'lobsters',
    'eggs', 'egg', 'fish', 'peanuts', 'soya', 'soy', 'soybeans', 'milk', 'nuts',
    'almonds', 'hazelnuts', 'walnuts', 'cashews', 'pecan', 'brazil nuts', 'pistachio',
    'macadamia', 'celery', 'mustard', 'sesame', 'sulphur dioxide', 'sulphites', 'sulfites',
    'lupin', 'molluscs', 'mussels', 'oysters', 'squid', 'snails', 'lecithins'
]

def latex_escape_ingredients(text: str) -> str:
    # Escape ingredients AFTER bold markers, escape FIRST to prevent truncation.
    text = str(text)
    # CRITICAL: Escape % FIRST to prevent LaTeX comment truncation...
    text = text.replace('%', '\\%')
    return text

def highlight_allergens_ingredients(ingredients_raw: str) -> str:
    # Wrap EU allergens in \textbf{}.
    text = ingredients_raw
    print(f"Original text: {text[:100]}...")
    for allergen in EU_ALLERGENS:
        pattern = r'\b' + re.escape(allergen) + r'\b'
        def bold_match(match):
            return r'\textbf{' + match.group(0) + '}'
        text = re.sub(pattern, bold_match, text, flags=re.IGNORECASE)
    print(f"Bolded text: {text[:100]}...")
    return text

def process_ingredients(ingredients_raw: str) -> str:
    # Highlight allergens, escape ingredients properly.
    # NOTE: Then escape for EGG -> EGG yolk...
    ingredients_marked = highlight_allergens_ingredients(ingredients_raw)
    # 1. Add bold markers FIRST (no escaping needed yet)...
    ingredients_tex = latex_escape_ingredients(ingredients_marked)
    print(f"TEX ingredients: {ingredients_tex[:150]}...")
    print('-' * 80)
    return ingredients_tex

def latex_escape_plain(text: str) -> str:
    # Escape for non-ingredients.
    if pd.isna(text):
        return ''
    text = str(text)
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def get_nutrition_table_row(row):
    if not bool(row.get('nutritionalinformation', False)):
        return ''
    def val(col):
        return latex_escape_plain(str(row.get(col, '')))
    return f'''\\begin{{tabular}}{{l r 2l}}
Nutritional Values per 100g &
Energy & {val('energykj')} & {val('energykcal')} \\\\
Fat & {val('fattotal')} & of which saturates & {val('fatsaturates')} \\\\
Carbohydrate & {val('carbohydrates')} & of which sugars & {val('sugars')} \\\\
Fiber & {val('fibre')} \\\\
Protein & {val('protein')} \\\\
Salt & {val('salt')} \\\\
\\end{{tabular}}'''

def main():
    df = pd.read_csv(CSVFILE)
    # Process ALL rows instead of just iloc[0]
    all_labels_tex = []
    for idx, row in df.iterrows():
        print(f"Processing row {idx}: {row.get('productname', 'Unnamed')}")
        # 2. Escape ingredients with protection...
        ingredients_tex = process_ingredients(row['listofingredients'])

        template_text = Path(TEXTEMPLATE).read_text(encoding='utf-8')
        placeholders = {
            'PRODUCTNAME': latex_escape_plain(row['productname']),
            'LISTOFINGREDIENTS': ingredients_tex,
            'BARCODENUMBER': latex_escape_plain(row['barcodenumber']),
            'NETQUANTITY': latex_escape_plain(row['netquantity']),
            'EMARK': latex_escape_plain(row['emark']),
            'DRAINEDWEIGHT': latex_escape_plain(row['drainedweight']),
            'BRANDLOGO': latex_escape_plain(row['brandlogo']),
            'BUSINESSADDRESS': latex_escape_plain(row['businessaddress']),
            'BESTBEFOREDATE': latex_escape_plain(row['bestbeforedate']),
        }
        final_tex = template_text
        for ph, val in placeholders.items():
            final_tex = final_tex.replace(f'@{ph}@', val)
        # Process ingredients FIRST...

        nutrition_table = get_nutrition_table_row(row)
        block = r'\\begin{tabular}{l r 2l} Nutritional Values per 100g Energy ENERGYKJ ENERGYKCAL Fat FATTOTAL of which saturates FATSATURATES Carbohydrate CARBOHYDRATES of which sugars SUGARS Fiber FIBRE Protein PROTEIN Salt SALT \\end{tabular}'
        if nutrition_table:
            final_tex = final_tex.replace(block, nutrition_table)
        else:
            start = r'\\begin{tikzpicture} \\draw[rounded corners=4pt,line width=0.4pt,inner sep=4pt,outer sep=0pt,anchor=north west] (box) at (0,0) {}; \\end{tikzpicture}'
            i = final_tex.find(start)
            if i != -1:
                j = final_tex.find('\\end{tikzpicture}', i) + len('\\end{tikzpicture}')
                final_tex = final_tex[:i] + final_tex[j:]

        all_labels_tex.append(final_tex)

    # Combine all labels with \newpage between them
    combined_tex = '\n\\newpage\n'.join(all_labels_tex)
    Path(OUTPUTTEX).write_text(combined_tex, encoding='utf-8')
    print(f"Wrote {OUTPUTTEX} with {len(df)} labels")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            tmppath / OUTPUTTEX.write_text(combined_tex, encoding='utf-8')
            for _ in range(2):
                subprocess.run(['pdflatex', '-interaction=nonstopmode', '-output-directory', str(tmppath), OUTPUTTEX], check=True, capture_output=True)
            shutil.copy2(tmppath / OUTPUTPDF, OUTPUTPDF)
        print(f"Created {OUTPUTPDF} - Full ingredients BOLD EGG!")
    except Exception as e:
        print(f"pdflatex error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()