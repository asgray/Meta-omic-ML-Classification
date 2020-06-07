from future.standard_library import install_aliases
install_aliases()
from urllib.request import urlopen
import json
from pprint import pprint
from terminaltables import AsciiTable
from go_utils import get_term

# compares dict and xml structures of info

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