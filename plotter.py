<<<<<<< HEAD
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()

parser = argparse.ArgumentParser(description='Plotter')
parser.add_argument('-d', '--data', type=str, required=True, help='Import dataset path')
args = parser.parse_args()

df = pd.read_csv(args.data)

sns.scatterplot(x='Data Treatment', y='Overall Accuracy',data=df, hue='Data Type', style= 'Dataset', s=110)
plt.title('Overall Classification Accuracy')
=======
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()

parser = argparse.ArgumentParser(description='Plotter')
parser.add_argument('-d', '--data', type=str, required=True, help='Import dataset path')
args = parser.parse_args()

df = pd.read_csv(args.data)

sns.scatterplot(x='Data Treatment', y='Overall Accuracy',data=df, hue='Data Type', style= 'Dataset', s=110)
plt.title('Overall Classification Accuracy')
>>>>>>> d11fed841e9ab9caa986f2a85b287800468216d2
plt.show()