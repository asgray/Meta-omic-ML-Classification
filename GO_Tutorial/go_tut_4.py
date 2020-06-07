from go_utils import get_ebi, get_GO
from pprint import pprint
from goatools.go_enrichment import GOEnrichmentStudy

# uses GOEnrichmentStudy() to demo 

arab_uri = '/pub/databases/GO/goa/ARABIDOPSIS/goa_arabidopsis.gaf.gz'
rec = get_ebi(arab_uri)

go = get_GO(optional_attrs=['relationship'])
# collect all growth functions from arabidopsis
keyword = 'growth'
growth_dict = {x: rec[x]
               for x in rec 
               if keyword in rec[x]['DB_Object_Name']}

# population set of genes
pop = rec.keys()

#  collect assocaitions between protein IDs and GO terms
assoc = {}
for x in rec:
    if x not in assoc:
        assoc[x] = set()
    assoc[x].add(str(rec[x]['GO_ID']))

# study set
study = growth_dict.keys()

methods = ["bonferroni", "sidak", "holm", "fdr"]
alpha = 0.01
# g = GOEnrichmentStudy(pop, assoc, go,
#                          propagate_counts=True,
#                          alpha=0.05,
#                          methods=methods)
# g = GOEnrichmentStudy(pop, assoc, go,
#                          propagate_counts=True,
#                          alpha=0.01,
#                          methods=['bonferroni'])
                         
g = GOEnrichmentStudy(pop, assoc, go,
                         propagate_counts=True,
                         alpha=0.05,
                         methods=['fdr'])

g_res = g.run_study(study)

goea_results_sig = [r for r in g_res if r.get_pvalue() <= alpha]
for res in goea_results_sig:
    print(res)