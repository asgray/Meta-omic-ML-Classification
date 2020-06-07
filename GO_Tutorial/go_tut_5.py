import math
from pprint import pprint
from collections import Counter
from go_utils import get_GO, deepest_common_ancestor, get_ebi

class TermCounts():
    '''
        TermCounts counts the term counts for each 
    '''
    def __init__(self, go, annots):
        '''
            Initialise the counts and  
        '''
        # Backup
        self._go = go
        
        # Initialise the counters
        self._counts = Counter()
        self._aspect_counts = Counter()
        
        # Fill the counters...
        self._count_terms(go, annots)
        
    def _count_terms(self, go, annots):
        '''
            Fills in the counts and overall aspect counts.
        '''
        for x in annots:
            # Extract term information
            go_id = annots[x]['GO_ID']
            try:
                namespace = go[go_id].namespace
                self._counts[go_id] += 1
                rec = go[go_id]
                parents = rec.get_all_parents()
                for p in parents:
                    self._counts[p] += 1
            
                self._aspect_counts[namespace] += 1
            except:
                print(f'Go ID {go_id} not found')
            
            
    def get_count(self, go_id):
        '''
            Returns the count of that GO term observed in the annotations.
        '''
        return self._counts[go_id]
        
    def get_total_count(self, aspect):
        '''
            Gets the total count that's been precomputed.
        '''
        return self._aspect_counts[aspect]
    
    def get_term_freq(self, go_id):
        '''
            Returns the frequency at which a particular GO term has 
            been observed in the annotations.
        '''
        try:
            namespace = self._go[go_id].namespace
            freq = float(self.get_count(go_id)) / float(self.get_total_count(namespace))
        except ZeroDivisionError:
            freq = 0
        
        return freq

def min_branch_length(go_id1, go_id2, go):
    '''
        Finds the minimum branch length between two terms in the GO DAG.
    '''
    # First get the deepest common ancestor
    dca = deepest_common_ancestor([go_id1, go_id2], go)
    
    # Then get the distance from the DCA to each term
    dca_depth = go[dca].depth
    d1 = go[go_id1].depth - dca_depth
    d2 = go[go_id2].depth - dca_depth
    
    # Return the total distance - i.e., to the deepest common ancestor and back.
    return d1 + d2

def semantic_distance(go_id1, go_id2, go):
    '''
        Finds the semantic distance (minimum number of connecting branches) 
        between two GO terms.
    '''
    return min_branch_length(go_id1, go_id2, go)

def semantic_similarity(go_id1, go_id2, go):
    '''
        Finds the semantic similarity (inverse of the semantic distance) 
        between two GO terms.
    '''
    return 1.0 / float(semantic_distance(go_id1, go_id2, go))

def ic(go_id, termcounts):
    '''
        Calculates the information content of a GO term.
    '''
    # Get the observed frequency of the GO term
    freq = termcounts.get_term_freq(go_id)

    # Calculate the information content (i.e., -log("freq of GO term")
    return -1.0 * math.log(freq)

def resnik_sim(go_id1, go_id2, go, termcounts):
    '''
        Computes Resnik's similarity measure.
    '''
    msca = deepest_common_ancestor([go_id1, go_id2], go)
    return ic(msca, termcounts)

go = get_GO()
arab_uri = '/pub/databases/GO/goa/ARABIDOPSIS/goa_arabidopsis.gaf.gz'
rec = get_ebi(arab_uri)

id1 = 'GO:0048364'
id2 = 'GO:0044707'
sim = semantic_similarity(id1, id2, go)
print(f'The semantic similarity between terms {id1} and {id2} is {sim}.') 

# First get the counts of each GO term.
termcounts = TermCounts(go, rec)
# Calculate the information content
infocontent = ic(id1, termcounts)
print(infocontent)

sim_r = resnik_sim(id1, id2, go, termcounts)
print(f'Resnik similarity score: {sim_r}')