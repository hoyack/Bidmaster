import os
import json
import subprocess
import csv
from odf.opendocument import load, OpenDocumentText
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

def modify_odt(template_odt, csv_file, output_folder, map_file):
    with open(map_file, "r") as file:
        mappings = json.load(file)
    
    with open(csv_file, 'r') as csv_data:
        reader = csv.DictReader(csv_data)
        to_remove = []  # List to store ODT filenames for later removal

        for row in reader:
            doc = load(template_odt)
            
            for paragraph in doc.getElementsByType(TextP):
                text_content = teletype.extractText(paragraph)
                modified_text_content = text_content  # This will store the potentially modified text

                for field, column_name in mappings['mergefields'].items():
                    if field in modified_text_content:
                        modified_text_content = modified_text_content.replace(field, row.get(column_name, ''))

                # If the paragraph text has been modified, then rebuild the paragraph
                if modified_text_content != text_content:
                    new_paragraph = TextP(text=modified_text_content)
                    paragraph.parentNode.insertBefore(new_paragraph, paragraph)
                    paragraph.parentNode.removeChild(paragraph)

            output_filename = os.path.join(output_folder, f"{row[mappings['filename']['FilenameA']]} - {row.get(mappings['filename']['FilenameB'], 'Unnamed')}.odt")
            doc.save(output_filename)
            print(f"Written: {output_filename}")
            
            # Convert to PDF
            odt_to_pdf(output_filename, output_folder)
            
            # Append the filename to to_remove list
            to_remove.append(output_filename)
            yield output_filename
        
        # Remove ODTs after processing all rows
        for filename in to_remove:
            if os.path.exists(filename):
                os.remove(filename)
