from go_utils import get_ebi
from pprint import pprint
from terminaltables import AsciiTable
from matplotlib import pyplot
import numpy
import kiwisolver

# Retrieves GO Terms from QuickGO browser, explore annotations

arab_uri = '/pub/databases/GO/goa/ARABIDOPSIS/goa_arabidopsis.gaf.gz'
rec = get_ebi(arab_uri)

not_count = 0
total_count = len(rec)
for func in rec.values():
    if 'NOT' in func['Qualifier']:
        not_count += 1

print(f'Total count of NOT qualifiers: {not_count} ({round(((float(not_count)/float(total_count))*100),2)}%)')
print(f'Total number of annotations: {total_count}')

arab_tax_id = 3702  # This isn't necessary here, but would be with the full data set.
go_id = 'GO:0048527'
annot_count = 0
counted_gene = []
for uniprot_id in rec:
    if('taxon:' + str(arab_tax_id) in rec[uniprot_id]['Taxon_ID']):
        if((rec[uniprot_id]['GO_ID'] == go_id)):
            counted_gene.append(uniprot_id)
            annot_count += 1
del counted_gene
print(f'annotation count of {go_id}: {annot_count}')

keyword = 'growth'
growth_dict = {x: rec[x]
               for x in rec 
               if keyword in rec[x]['DB_Object_Name']}
print(f'UniProt IDs of annotations with "{keyword}" in their name:')
for annot in growth_dict:
    print("\t - " + annot)
print(f"Total: {len(growth_dict)}")

evidence_count = {}
for annotation in rec:
    evidence = rec[annotation]['Evidence']
    
    if(evidence not in evidence_count):
        evidence_count[evidence] = 1
    else:
        evidence_count[evidence] += 1

table_data = [['Evidence Code', 'Count']]
for code in sorted(evidence_count.keys()):
    table_data.append([code, str(evidence_count[code])])
print(AsciiTable(table_data).table)

evidence_percent = {}
for code in evidence_count:
        evidence_percent[code] = ((float(evidence_count[code]) /
                                   float(total_count))
                                  *100)

table_data = [['Evidence Code', 'Count', 'Percentage (%)']]
for code in sorted(evidence_count.keys()):
    table_data.append([code, str(evidence_count[code]), str(round(evidence_percent[code],2))])
print(AsciiTable(table_data).table)

# Setup the figure
fig = pyplot.figure(1, figsize=(8,8), dpi=96)
ax=fig.add_axes([0.1,0.1,0.8,0.8])

# Extract the lables / percentages
labels = evidence_percent.keys()
fracs = evidence_percent.values()

# Make IEA obvious by "exploding" it
explode = [int('IEA' in x)*0.1 for x in labels]

# Plot the pie chart
patches, texts = ax.pie(list(fracs), explode=explode, startangle=90, labeldistance=1.1) 

# Add 
ax.legend(patches, labels, bbox_to_anchor=(1.2, 0.75), fontsize=12)
pyplot.show()