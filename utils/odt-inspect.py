import argparse
import zipfile
import os

def unzip_odt(odt_file, output_folder):
    with zipfile.ZipFile(odt_file, 'r') as zip_ref:
        zip_ref.extractall(output_folder)
        print(f"Unzipped contents of {odt_file} saved to: {output_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unzip an ODT file into the specified directory.")
    parser.add_argument("-odt", required=True, help="ODT file to be unzipped.")
    args = parser.parse_args()

    # Use the current working directory as the output directory
    output_dir = os.path.splitext(args.odt)[0]
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    unzip_odt(args.odt, output_dir)