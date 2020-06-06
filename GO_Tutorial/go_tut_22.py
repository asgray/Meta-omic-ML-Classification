from go_utils import get_GO
from goatools import obo_parser
from IPython.display import Image

# BROKEN
# pygraphviz does not install

go_obo = get_GO()
go = obo_parser.GODag(go_obo)

go_id = 'GO:0097190'
rec = go[go_id]

lineage_png = go_id + '-lineage.png'

go.draw_lineage([rec])

Image(lineage_png)