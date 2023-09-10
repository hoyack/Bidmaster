import csv
import os
import argparse
import json
from copy import deepcopy
from odf import text, teletype
from odf.opendocument import load
import subprocess

def load_mappings(mappings_file='map.json'):
    with open(mappings_file, 'r') as f:
        return json.load(f)

def modify_odt(template_file, csv_file, folder, should_print):
    mappings = load_mappings()
    
    # Load the template ODT file
    template = load(template_file)

    # Ensure the output directory exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Read the CSV and for each row, replace and save the ODT
    with open(csv_file, 'r') as csv_f:
        reader = csv.DictReader(csv_f)
        for row in reader:
            # Make a deep copy of the document
            doc = deepcopy(template)

            replacements = []
            for paragraph in doc.text.getElementsByType(text.P):
                inner_text = teletype.extractText(paragraph)
                replaced = False
                for placeholder, csv_column in mappings['mergefields'].items():
                    if placeholder in inner_text and csv_column in row:
                        inner_text = inner_text.replace(placeholder, row[csv_column])
                        replaced = True
                if replaced:
                    replacements.append((paragraph, text.P(text=inner_text)))

            # Apply the replacements
            for old_paragraph, new_paragraph in replacements:
                doc.text.insertBefore(new_paragraph, old_paragraph)
                doc.text.removeChild(old_paragraph)

            # Determine the output filename and save
            output_filename = os.path.join(folder, f"{row[mappings['filename']['FilenameA']]} - {row.get(mappings['filename']['FilenameB'], 'Unnamed')}.odt")
            doc.save(output_filename)
            print(f"Written: {output_filename}")

            # Convert to PDF and remove the ODT
            odt_to_pdf(output_filename, folder)
            os.remove(output_filename)

    if should_print:
        print_files(folder)


def odt_to_pdf(odt_file, output_folder):
    # Convert using LibreOffice
    subprocess.run(["libreoffice", "--headless", "--convert-to", f"pdf:writer_pdf_Export", odt_file, "--outdir", output_folder])

def print_files(directory):
    files = os.listdir(directory)
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    for pdf_file in pdf_files:
        subprocess.run(['lp', os.path.join(directory, pdf_file)])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace placeholders in an ODT file using a CSV based on a JSON mapping.")
    parser.add_argument("-odt", required=True, help="Path to the ODT file.")
    parser.add_argument("-csv", required=True, help="Path to the CSV file.")
    parser.add_argument("-f", required=True, help="Output folder name.")
    parser.add_argument("-print", action="store_true", help="Print the PDF files after creation.")

    args = parser.parse_args()
    modify_odt(args.odt, args.csv, args.f, args.print)
