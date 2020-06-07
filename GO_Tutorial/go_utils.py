import os
import wget
import gzip
from ftplib import FTP
from goatools import obo_parser
import Bio.UniProt.GOA as GOA

def get_GO(optional_attrs=None):
    '''
    Fetches GO Basic to local file if not present
    Returns GO Basic file
    '''
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
    go = obo_parser.GODag(go_obo, optional_attrs=optional_attrs)
    return go

def get_ebi(uri):
    '''
    Fetches GOA file for a species from UniProt using Biopython
    Retrurns annotations 
    '''
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

def get_term(go_id):
    """
        This function retrieves the definition of a given Gene Ontology term,
        using EMBL-EBI's QuickGO browser.
        Input: go_id - a valid Gene Ontology ID, e.g. GO:0048527.
    """
    quickgo_url = "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/" + go_id
    ret = urlopen(quickgo_url)
    
    # Check the response
    if(ret.getcode() == 200):
        term = json.loads(ret.read())
        return term['results'][0]
    else:
        raise ValueError("Couldn't receive information from QuickGO. Check GO ID and try again.")

def common_parent_go_ids(terms, go):
    '''
        This function finds the common ancestors in the GO 
        tree of the list of terms in the input.
    '''
    # Find candidates from first
    rec = go[terms[0]]
    candidates = rec.get_all_parents()
    candidates.update({terms[0]})
    
    # Find intersection with second to nth term
    for term in terms[1:]:
        rec = go[term]
        parents = rec.get_all_parents()
        parents.update({term})
        
        # Find the intersection with the candidates, and update.
        candidates.intersection_update(parents)
        
    return candidates

def deepest_common_ancestor(terms, go):
    '''
        This function gets the nearest common ancestor 
        using the above function.
        Only returns single most specific - assumes unique exists.
    '''
    # Take the element at maximum depth. 
    return max(common_parent_go_ids(terms, go), key=lambda t: go[t].depth)