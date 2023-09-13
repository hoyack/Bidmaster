import csv
import os
import argparse
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

def avery_5195(csv_file):
    PAGE_WIDTH, PAGE_HEIGHT = letter  # Define page dimensions first
    
    # Label dimensions
    WIDTH, HEIGHT = 1.6929*inch, 0.6299*inch + 0.03937*inch  # Added 0.1 cm to the HEIGHT

    # Updated margins
    MARGIN_TOP, MARGIN_LEFT = 0.5906*inch, 0.4724*inch

    COLUMNS, ROWS = 4, 15
    FONT_SIZE = 8

    column_adjustments = [0, 0.3937*inch, 2*0.3937*inch, 3*0.3937*inch]  # Adjustments for the 2nd, 3rd, and 4th columns in inches

    records = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for record in reader:
            records.append(record)

    c = canvas.Canvas("labels.pdf", pagesize=letter)
    c.setFont("Helvetica", FONT_SIZE)
    
    row, col = 0, 0

    for record in records:
        x = MARGIN_LEFT + (WIDTH * col) + column_adjustments[col]
        y = PAGE_HEIGHT - MARGIN_TOP - (HEIGHT * row) + (0.01*inch * row)  # Adjusted increment

        # Placing the text on the label
        c.drawString(x, y - 8, record['Company'])
        c.drawString(x, y - 20, record['Address 1'])
        c.drawString(x, y - 32, record['Address 2'])
        c.drawString(x, y - 44, f"{record['City']}, {record['State']}, {record['Zip']}")

        col += 1
        if col >= COLUMNS:
            col = 0
            row += 1
        if row >= ROWS:
            c.showPage()
            row, col = 0, 0

    c.save()




def avery_5260(csv_file):
    WIDTH, HEIGHT = 2.625*inch, 1*inch
    MARGIN_TOP, MARGIN_LEFT = 0.5*inch, 0.1875*inch
    COLUMNS, ROWS = 3, 10
    PAGE_WIDTH, PAGE_HEIGHT = letter
    
    c = canvas.Canvas("labels.pdf", pagesize=letter)
    c.setFont("Helvetica", 10)

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        row, col = 0, 0

        for record in reader:
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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # This will point to the parent of the current script's directory

    parser = argparse.ArgumentParser(description='Generate and print labels from CSV based on Avery type.')
    parser.add_argument('-csv', required=True, help='Path to the CSV file.')
    parser.add_argument('-avery', type=int, choices=[5260, 5195], required=True, help='Specify Avery label type.')

    args = parser.parse_args()

    # If the provided path is not absolute, assume it's within the sources directory
    if not os.path.isabs(args.csv):
        args.csv = os.path.join(base_dir, 'sources', args.csv)

    if args.avery == 5260:
        avery_5260(args.csv)
    elif args.avery == 5195:
        avery_5195(args.csv)

    print_labels()

