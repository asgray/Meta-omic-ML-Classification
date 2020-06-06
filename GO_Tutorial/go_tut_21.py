from go_utils import get_GO
from goatools import obo_parser
from pprint import pprint


go_obo = get_GO()
go = obo_parser.GODag(go_obo, optional_attrs=['relationship'])

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

go_id1 = 'GO:0097178'
go_id_id1_dca = deepest_common_ancestor([go_id, go_id1], go)
print(f'The nearest common ancestor of\n\t{go_id} ({go[go_id].name})\nand\n\t{go_id1} ({go[go_id1].name})\nis\n\t{go_id_id1_dca} ({go[go_id_id1_dca].name})')

go_id3 = 'GO:0007124'
pprint(go[go_id3].get_goterms_upper_rels('regulates'))
print('\n lower \n')
pprint(go[go_id3].get_goterms_lower_rels('regulates'))