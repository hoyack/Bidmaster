import os
import json
import subprocess
import csv
from odf.opendocument import load
from odf.text import P as TextP
from odf import teletype

def odt_to_pdf(odt_path, output_folder):
    output_pdf = os.path.join(output_folder, os.path.splitext(os.path.basename(odt_path))[0] + '.pdf')
    command = [
        'libreoffice',
        '--headless',
        '--convert-to',
        'pdf',
        '--outdir',
        output_folder,
        odt_path
    ]
    subprocess.run(command)
    return output_pdf

def recursive_replace(node, mappings, row):
    if node.nodeType == node.TEXT_NODE:
        text_content = node.data
        for field, column_name in mappings['mergefields'].items():
            if field in text_content:
                print(f"Attempting to replace '{field}' with '{row.get(column_name, 'No matching CSV column')}'")
                text_content = text_content.replace(field, row.get(column_name, ''))
        node.data = text_content

    for child in node.childNodes:
        recursive_replace(child, mappings, row)

def modify_odt(template_odt, csv_file, output_folder, map_file):
    with open(map_file, "r") as file:
        mappings = json.load(file)
    
    with open(csv_file, 'r') as csv_data:
        reader = csv.DictReader(csv_data)
        to_remove = []

        for row in reader:
            doc = load(template_odt)
            for paragraph in doc.getElementsByType(TextP):
                recursive_replace(paragraph, mappings, row)

            output_filename = os.path.join(output_folder, f"{row[mappings['filename']['FilenameA']]} - {row.get(mappings['filename']['FilenameB'], 'Unnamed')}.odt")
            doc.save(output_filename)
            
            print(f"Written: {output_filename}")
            
            odt_to_pdf(output_filename, output_folder)
            to_remove.append(output_filename)
            yield output_filename
        
        for filename in to_remove:
            if os.path.exists(filename):
                os.remove(filename)