from future.standard_library import install_aliases
install_aliases()
from urllib.request import urlopen
import json
from pprint import pprint
from terminaltables import AsciiTable

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

id1 = 'GO:0048527'
id2 = 'GO:0097178'

rec1 = get_term(id1)
rec2 = get_term(id2)

# pprint(rec)

print(f"Name: {rec1['name']}")
print(f"Description : {rec1['definition']['text']}")

synonyms = rec2['synonyms']
# Initialise table data and set header
table_data = [['Type', 'Synonym']]
for synonym in synonyms:
    table_data.append([synonym['type'], synonym['name']])
print(AsciiTable(table_data).table)