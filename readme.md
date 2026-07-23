Steps to create the dataset as is:
- Download first page of ied_works as a csv
- Use split_ied_works.py to create two separate csv files: gregil.csv and dsbc.csv

For Gretil:
- Download Gretil data from https://github.com/sanskrit-texts/gretil-corpus
- gretil_compare_xml_to_bn_filelist.py: This script will (1) produce a csv file with a list of filenames in gretil_sa folder and their corresponding ".htm" references; (2) update gretil.csv to include columns for those file names, matched with the Buddha Nexus data where possible; (3) output some data on which files are missing / added in both dataets
- gretil_track_dsbc_in_gretil: Adds a column to gretil.csv indicating which files are originally from dsbc.
- gretil_find_body_tags.py: produces a full list of TEI tags in the gretil files.
- gretil_produce_plain_txt.py: extracts body text from the gretil xml corpus and produces plain text versions. 

For DSBC:
- Download complete index of all works (raw html from https://www.dsbcproject.org/canon-text/browse-by-list/1)
- dsbc_links_titles_from_index.py: creates src/dsbc/texts.csv, which contains links and titles as given in the index.html.
- dsbc_download_texts.py: downloads all linked html pages, saves them in "book" folders
- dsbc_html_to_xml.py: saves corpus to corpus, extracts typist names and puts them in a TEI header, removes all html tags. Also puts the url and title as given in index.html in the TEI header.
- dsbc_produce_plain_txt.py: 
