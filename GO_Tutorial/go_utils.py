import os
import wget
import gzip
from ftplib import FTP
from goatools import obo_parser
import Bio.UniProt.GOA as GOA

def get_GO():
    go_obo_url = 'http://purl.obolibrary.org/obo/go/go-basic.obo'
    data_folder = os.getcwd() + '/data'

    # Check if we have the ./data directory already
    if(not os.path.isfile(data_folder)):
        # Emulate mkdir -p (no error if folder exists)
        try:
            os.mkdir(data_folder)
        except OSError as e:
            if(e.errno != 17):
                raise e
    else:
        raise Exception('Data path (' + data_folder + ') exists as a file. '
                    'Please rename, remove or change the desired location of the data path.')

    # Check if the file exists already
    if(not os.path.isfile(data_folder+'/go-basic.obo')):
        go_obo = wget.download(go_obo_url, data_folder+'/go-basic.obo')
    else:
        go_obo = data_folder+'/go-basic.obo'

    return go_obo

def get_ebi(uri):
    data_folder = os.getcwd() + '/data'
    fn = uri.split('/')[-1]
    # Check if the file exists already
    gaf = os.path.join(data_folder, fn)
    if(not os.path.isfile(gaf)):
        # Login to FTP server
        ebi_ftp = FTP('ftp.ebi.ac.uk')
        ebi_ftp.login() # Logs in anonymously
        
        # Download
        with open(gaf,'wb') as fp:
            ebi_ftp.retrbinary(f'RETR {uri}', fp.write)
            
        # Logout from FTP server
        ebi_ftp.quit()
    # File is a gunzip file, so we need to open it in this way
    with gzip.open(gaf, 'rt') as gaf_fp:
        funcs = {}  # Initialise the dictionary of functions
        
        # Iterate on each function using Bio.UniProt.GOA library.
        for entry in GOA.gafiterator(gaf_fp):
            uniprot_id = entry.pop('DB_Object_ID')
            funcs[uniprot_id] = entry
    return funcs