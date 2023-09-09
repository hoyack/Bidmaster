import subprocess
import os

def print_files(directory):
    files = os.listdir(directory)
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]

    for pdf_file in pdf_files:
        subprocess.run(['lp', os.path.join(directory, pdf_file)])

if __name__ == "__main__":
    print_files(os.getcwd())