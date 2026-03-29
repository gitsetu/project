# Label Automator

Exploration of 3 different approaches (scripting, coding and AI prompting) for automating EU compliant label designs:

- Illustrator Scripting
- Python
- AI prompting

## Illustrator Scripting

This script can import data from a CSV file into a working document in Adobe Illustrator. Written in JavaScript ES3 it is compatible with Adobe CS6.

#### Requirements:

1. Adobe Illustrator installed.
2. Spreadsheet application or CSV file with data.

#### How to use:

1. From your spreadsheet application export the desired data as CSV file.
2. Start Adobe Illustrator, have a working document open, on the application menu select File > Open or File > New.
3. On the application menu select File > Scripts > Other Scripts and select the JSX file. The script will prompt for the CSV file location, select the file and the data will be imported on the working document.

## Python

Requirements:

1. Python version 3 installed.  
   `https://www.python.org/downloads/`

2. Libraries Pandas and PyLaTeX installed.  
   `pip install pandas pylatex`

3. A LaTeX distribution installed such as MacTeX, TeX Live, or MiKTeX. Necessary to compile the PDF.  
   `https://www.latex-project.org/get/`

#### How to use:

Put the necessary files into the same directory:

- generate-labels.py
- label-template.tex
- brand-logo.png
- products.csv

Open the terminal of your system and enter the command:  
`python generate-label.py`

After running the command two files for each product will be created on their own directory, one with the extension `.tex` and another with the extension `.pdf`. The TeX file contains the instructions that creates the PDF.

## AI Prompting

No code here, just a short selection of prompts.  
[AI Prompting](ai/prompt.md)
