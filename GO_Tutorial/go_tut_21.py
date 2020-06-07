from go_utils import get_GO, deepest_common_ancestor
from pprint import pprint

# Load and investigate GO basic local file 

go = get_GO(optional_attrs=['relationship'])

# Excercise 2.1
go_id = 'GO:0048527'
go_term = go[go_id]
print(go_term)
print(f'GO term name: {go_term.name}')
print(f'GO term namespace: {go_term.namespace}')
print('Parents: ')
for term in go_term.parents:
    print(term)
print('Children: ')
for term in go_term.children:
    print(term)

parents = go_term.get_all_parents()
children = go_term.get_all_children()
print('All parents and children')
for term in parents.union(children):
    print(go[term])

growth_count = 0
for term in go.values():
    if 'growth' in term.name:
        growth_count += 1
        
print(f'Number of GO terms with "growth" in their name: {growth_count}')

go_id1 = 'GO:0097178'
go_id_id1_dca = deepest_common_ancestor([go_id, go_id1], go)
print(f'The nearest common ancestor of\n\t{go_id} ({go[go_id].name})\nand\n\t{go_id1} ({go[go_id1].name})\nis\n\t{go_id_id1_dca} ({go[go_id_id1_dca].name})')

go_id3 = 'GO:0007124'
pprint(go[go_id3].get_goterms_upper_rels('regulates'))
print('\n lower \n')
pprint(go[go_id3].get_goterms_lower_rels('regulates'))