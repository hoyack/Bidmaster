import csv
import os
import argparse
import subprocess
import json
from copy import deepcopy
from odf import text, teletype
from odf.opendocument import load

def modify_odt(template_file, csv_file, folder, should_print):
    # Load the template ODT file
    template = load(template_file)

    # Ensure the output directory exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Load mapping data from map.json
    with open("map.json", "r") as map_file:
        mappings = json.load(map_file)
        mergefields = mappings["mergefields"]
        filename_mapping = mappings["filename"]

    # Read the CSV and for each row, replace and save the ODT
    with open(csv_file, 'r') as csv_f:
        reader = csv.DictReader(csv_f)
        for row in reader:
            # Make a deep copy of the document
            doc = deepcopy(template)

            # Collect paragraphs that need modification
            paragraphs_to_modify = []
            for paragraph in doc.text.getElementsByType(text.P):
                inner_text = teletype.extractText(paragraph)
                if any(key in inner_text for key in mergefields.keys()):
                    paragraphs_to_modify.append(paragraph)

            # Replace the placeholders
            for paragraph in paragraphs_to_modify:
                inner_text = teletype.extractText(paragraph)
                for key, value in mergefields.items():
                    inner_text = inner_text.replace(key, row[value])
                
                new_paragraph = text.P(text=inner_text)
                parent = paragraph.parentNode
                parent.insertBefore(new_paragraph, paragraph)
                parent.removeChild(paragraph)

            # Determine the output filename and save
            output_filename = os.path.join(folder, f"{row[filename_mapping['FilenameA']]} - {row.get(filename_mapping['FilenameB'], 'Unnamed')}.odt")
            doc.save(output_filename)
            print(f"Written: {output_filename}")

            # Convert to PDF and remove the ODT
            odt_to_pdf(output_filename, folder, should_print)
            os.remove(output_filename)

def odt_to_pdf(odt_file, output_folder, should_print):
    # Convert using LibreOffice
    subprocess.run(["libreoffice", "--headless", "--convert-to", f"pdf:writer_pdf_Export", odt_file, "--outdir", output_folder])
    pdf_file = os.path.join(output_folder, os.path.splitext(os.path.basename(odt_file))[0] + ".pdf")
    if should_print:
        print_file(pdf_file)

def print_file(pdf_file):
    subprocess.run(['lp', pdf_file])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace placeholders in an ODT file using a CSV and map from JSON.")
    parser.add_argument("-odt", required=True, help="Path to the ODT file.")
    parser.add_argument("-csv", required=True, help="Path to the CSV file.")
    parser.add_argument("-f", required=True, help="Output folder name.")
    parser.add_argument("-print", action='store_true', help="Print generated PDFs.")

    args = parser.parse_args()
    modify_odt(args.odt, args.csv, args.f, args.print)
