import csv
import os
import argparse
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

def generate_labels_from_csv(csv_file):
    # Adjusted label dimensions
    WIDTH, HEIGHT = 2.625*inch, 1*inch
    MARGIN_TOP, MARGIN_LEFT = 0.5*inch, 0.1875*inch
    COLUMNS, ROWS = 3, 10
    PAGE_WIDTH, PAGE_HEIGHT = letter

    c = canvas.Canvas("labels.pdf", pagesize=letter)
    c.setFont("Helvetica", 10)  # Setting the font to Helvetica with size 10 pt

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        row, col = 0, 0
        
        for record in reader:
            # Adjust height based on row to compensate for drift
            if row >= 4:  # Because we start counting from 0
                HEIGHT += 0.00092*inch  # Subtracting 0.125mm from HEIGHT for each row starting from the 5th
                
            x = MARGIN_LEFT + (WIDTH * col)
            y = PAGE_HEIGHT - MARGIN_TOP - (HEIGHT * row)

            # Design the label centered with tighter spacing
            c.drawCentredString(x + WIDTH/2, y - 12, record['Company Name'])
            c.drawCentredString(x + WIDTH/2, y - 27, "Attn: " + record['Name'])
            c.drawCentredString(x + WIDTH/2, y - 42, record['Street Address 1'])
            c.drawCentredString(x + WIDTH/2, y - 57, f"{record['City']}, {record['State']} {record['Postal Code']}")

            col += 1
            if col >= COLUMNS:
                col = 0
                row += 1

            if row >= ROWS:
                c.showPage()
                row, col = 0, 0

    c.save()

def print_labels():
    subprocess.run(['lp', 'labels.pdf'])
    os.remove('labels.pdf')  # Delete the labels.pdf file after printing

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # This will point to basedir

    parser = argparse.ArgumentParser(description='Generate and print labels from CSV.')
    parser.add_argument('-csv', help='Path to the CSV file.', required=True)

    args = parser.parse_args()

    # If the provided path is not absolute, assume it's within the sources directory
    if not os.path.isabs(args.csv):
        args.csv = os.path.join(base_dir, 'sources', args.csv)

    generate_labels_from_csv(args.csv)
    print_labels()
