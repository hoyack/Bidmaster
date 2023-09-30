# Bidmaster
Performs Mail Merges and Prints Labels using LibreOffice Writer and a CSV file.
Prints to system default printer if the `-print` flag is provided.

#Installation
#Tested on Debian
```
sudo apt-get install libreoffice
sudo apt-get install python3
sudo apt-get install libcups2-dev
pip install virtualenv
git clone https://github.com/hoyack/Bidmaster.git
cd Bidmaster
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Run the following code to perform a mail merge:
`python mailmerge.py -odt template.odt -csv source.csv -f foldername -map map.json -print`

Run the following code to print labels (Currently Avery 5260 template is supported)
`python labels.py -csv source.csv`

place .ODT file template in /templates and .CSV source in /sources

-odt is the template filename of the .ODT file you want to use
-csv is the source CSV file you want to use
-map is a .json mapping file you will specifiy
-f is folder name you want to write PDF files to
-print will print PDF files to system default printer as they are generated

For mapping, specify the ODT template's placeholders you want to map
Specify which CSV column name you want to map a given placeholder to

For example:

if `{{first name}}` appears in the ODT you can map it to the `First Name` field in your CSV.
You can add multiple custom mappings.

The map.json example includes 2 sections. The 1st is the fields to mailmerge.
The 2nd is the filename structure to write.
The default format is "FieldA - FieldB.pdf"
    To modify this format, the change would be made to /utils/odt_modifier.py around line 43.

Logo.png for return labels should be 171x171 px

Usage:

# Pull Batch
python utils/process.py -o batch.csv --batch 30

# Add WIP Flag to Batch
python utils/keap.py -csv batch.csv --action 3

# Generate Shipping Labels
python utils/labels.py -csv batch.csv -avery 5260

# Run Mail Merge
python mailmerge.py -odt template.odt -csv batch.csv -f output -print

# Generate Return Labels
python utils/labels.py -csv return.csv -avery 5195

# Mark Sent
python utils/keap.py -csv batch.csv --action 2

# Remove WIP Flag
python utils/keap.py -csv batch.csv --action 1

# Delete Cache
python utils/keap.py -csv batch.csv --action 5