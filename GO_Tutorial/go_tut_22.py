from go_utils import get_GO
from IPython.display import Image

# BROKEN
# pygraphviz does not install
# supposed to produce graph of GO terms

go = get_GO()

go_id = 'GO:0097190'
rec = go[go_id]

lineage_png = go_id + '-lineage.png'

go.draw_lineage([rec])

Image(lineage_png)