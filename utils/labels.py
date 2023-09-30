import csv
import os
import argparse
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from reportlab.lib.utils import ImageReader
import urllib.request

def fetch_image_from_url(url):
    """
    Fetches an image from a URL and returns an ImageReader object.
    """
    # Use a context manager to fetch the image from the URL
    with urllib.request.urlopen(url) as response:
        # Create and return an ImageReader object from the fetched data
        return ImageReader(response)

def avery_5195(csv_file):
    PAGE_WIDTH, PAGE_HEIGHT = letter
    # Label dimensions
    WIDTH, HEIGHT = 1.6929*inch, 0.6299*inch + 0.03937*inch

    # Margins
    LINE_HEIGHT = 8  # Approximate height for one line with the given font size
    MARGIN_TOP, MARGIN_LEFT = 0.5906*inch - 0.3937*inch + (LINE_HEIGHT/72.0*inch), 0.4724*inch  # Adjusted the top margin by 1 cm and one line height

    COLUMNS, ROWS = 4, 15
    FONT_SIZE = 8
    LOGO_PADDING = 0.03937*inch
    column_adjustments = [0, 0.3937*inch, 2.035*0.3937*inch, 3.005*0.3937*inch]
    LOGO_SHIFT_LEFT = 1 * 0.295275*inch  # Shift logo 1 cm to the left
    TEXT_SHIFT_LEFT = 0.1 * 0.7874*inch  # Shift text 1/10 cm to the left

    CONTENT_START_Y_OFFSET = 0.1*inch  # 1/10th of an inch from top of each label

    def compute_drift(row):
        # This will compute a progressive drift. Row 1 will have minimal drift, 
        # and by row 15, the cumulative effect will be the full drift amount.
        MAX_DRIFT = 0.25*inch - 0.05*inch  # Adjusted the maximum drift value
        return MAX_DRIFT * (row/15.0)

    records = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for record in reader:
            records.append(record)

    c = canvas.Canvas("labels.pdf", pagesize=letter)
    c.setFont("Helvetica", FONT_SIZE)

    row, col = 0, 0

    for idx, record in enumerate(records):
        x = MARGIN_LEFT + (WIDTH * col) + column_adjustments[col]
        y = PAGE_HEIGHT - MARGIN_TOP - (HEIGHT * row) - CONTENT_START_Y_OFFSET - compute_drift(row)

        # Fetch logo from URL mentioned in the CSV
        logo_url = record.get('Logo', None)
        if logo_url:
            logo = fetch_image_from_url(logo_url)
            original_logo_width = HEIGHT - (2 * LOGO_PADDING)
            logo_width = original_logo_width * 0.5
            logo_height = original_logo_width * 0.5

            x_adjusted_for_logo = x + (original_logo_width - logo_width) / 2 - LOGO_SHIFT_LEFT
            y_adjusted_for_logo = y - (HEIGHT + logo_height) / 2

            c.drawImage(logo, x_adjusted_for_logo, y_adjusted_for_logo, width=logo_width, height=logo_height)
            text_start_x = x + logo_width + (2 * LOGO_PADDING) - TEXT_SHIFT_LEFT
        else:
            text_start_x = x

        # Drawing text fields
        c.drawString(text_start_x, y - 8, record['Company'])
        c.drawString(text_start_x, y - 20, record['Address 1'])
        c.drawString(text_start_x, y - 32, record['Address 2'])
        c.drawString(text_start_x, y - 44, f"{record['City']}, {record['State']}, {record['Zip']}")

        col += 1
        if col >= COLUMNS:
            col = 0
            row += 1
        if row >= ROWS:
            if idx != len(records) - 1:  # Only add a new page if this isn't the last record
                c.showPage()
                c.setFont("Helvetica", FONT_SIZE)  # Reset the font size for the new page
                row, col = 0, 0

    c.save()

def avery_5260(csv_file):
    # Label dimensions
    WIDTH, HEIGHT = 2.625*inch, 1*inch
    MARGIN_TOP, MARGIN_LEFT = 0.5*inch, 0.1875*inch
    COLUMNS, ROWS = 3, 10
    FONT_SIZE = 10
    PAGE_WIDTH, PAGE_HEIGHT = letter
    
    DRIFT_ADJUSTMENT = 0.02*inch  # Adjust this value based on the observed drift
    
    c = canvas.Canvas("labels.pdf", pagesize=letter)
    c.setFont("Helvetica", FONT_SIZE)

    records = []  # Collecting records to list to help with determining the last record
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for record in reader:
            records.append(record)

    row, col = 0, 0

    for idx, record in enumerate(records):
        x = MARGIN_LEFT + (WIDTH * col)
        y = PAGE_HEIGHT - MARGIN_TOP - (HEIGHT * row) - (DRIFT_ADJUSTMENT * row)  # Adjusted for drift
            
        if col == 2:  # Adjust for the third column (0-based indexing)
            x += 0.3937*inch

        # Design the label centered with tighter spacing
        c.drawCentredString(x + WIDTH/2, y - 12, record['Company Name'])
        c.drawCentredString(x + WIDTH/2, y - 24, "Attn: " + record['Name'])  # Reduced the gap
        c.drawCentredString(x + WIDTH/2, y - 36, record['Street Address 1'])  # Moved upwards
        c.drawCentredString(x + WIDTH/2, y - 48, f"{record['City']}, {record['State']} {record['Postal Code']}")  # Moved upwards

        col += 1
        if col >= COLUMNS:
            col = 0
            row += 1
        if row >= ROWS:
            if idx != len(records) - 1:  # Only add a new page if this isn't the last record
                c.showPage()
                c.setFont("Helvetica", FONT_SIZE)  # Reset the font size for the new page
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