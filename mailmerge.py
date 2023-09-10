import argparse
import os
import subprocess
from utils.odt_modifier import modify_odt

def odt_to_pdf(odt_file, output_folder):
    # Convert using LibreOffice
    subprocess.run(["libreoffice", "--headless", "--convert-to", f"pdf:writer_pdf_Export", odt_file, "--outdir", output_folder])

def print_pdf(pdf_file):
    subprocess.run(['lp', pdf_file])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modify an ODT template using a CSV and optional mapping.")
    parser.add_argument("-odt", required=True, help="ODT template filename. It should be inside the 'templates' directory.")
    parser.add_argument("-csv", required=True, help="CSV source filename. It should be inside the 'sources' directory.")
    parser.add_argument("-f", required=True, help="Output folder name.")
    parser.add_argument("-map", default="map.json", help="Mapping filename. It should be inside the 'maps' directory.")
    parser.add_argument("-print", action="store_true", help="Print the PDFs after creation.")

    args = parser.parse_args()

    # Prefix the paths with the respective directories
    template_path = os.path.join("templates", args.odt)
    csv_path = os.path.join("sources", args.csv)
    map_path = os.path.join("maps", args.map)

    if not os.path.exists(args.f):
        os.mkdir(args.f)

    for odt_output in modify_odt(template_path, csv_path, args.f, map_path):
        pdf_output = os.path.splitext(odt_output)[0] + ".pdf"
        odt_to_pdf(odt_output, args.f)
        os.remove(odt_output)
        if args.print:
            print_pdf(pdf_output)
