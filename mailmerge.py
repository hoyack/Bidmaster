import csv
import os
import argparse
from copy import deepcopy
from odf import text, teletype
from odf.opendocument import load
import subprocess

def modify_odt(template_file, csv_file, folder, should_print=False):
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

            # Replace the placeholder
            for paragraph in doc.text.getElementsByType(text.P):
                inner_text = teletype.extractText(paragraph)
                replaced_text = inner_text.replace("{{First Name}}", row['First Name'])
                if replaced_text != inner_text:
                    new_paragraph = text.P(text=replaced_text)
                    doc.text.insertBefore(new_paragraph, paragraph)
                    doc.text.removeChild(paragraph)

            # Determine the output filename and save
            output_filename = os.path.join(folder, f"{row['First Name']} - {row['Company Name']}.odt")
            doc.save(output_filename)
            print(f"Written: {output_filename}")
            
            # Convert to PDF and remove the ODT
            odt_to_pdf(output_filename, folder)
            os.remove(output_filename)
    
    # Print the generated PDFs if the flag is provided
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
    parser = argparse.ArgumentParser(description="Replace {{First Name}} in an ODT file using a CSV and optionally print the generated PDFs.")
    parser.add_argument("-odt", required=True, help="Path to the ODT file.")
    parser.add_argument("-csv", required=True, help="Path to the CSV file.")
    parser.add_argument("-f", required=True, help="Output folder name.")
    parser.add_argument('-print', action='store_true', help="Print the generated PDFs if provided.")

    args = parser.parse_args()
    modify_odt(args.odt, args.csv, args.f, args.print)