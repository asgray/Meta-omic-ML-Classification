# Anthony Gray
# AS.410.734.81
# Metagenomics Final Project

# This script operates on data files to produce modified data files, visualizations, and quality control

import csv
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import scipy.cluster.hierarchy as sch
from sklearn.preprocessing import StandardScaler

# method applies standard scaling to dataframe and saves to a new file -------------------------------------------------------------------------------
def standardize_data(df, output):
    samps = df['sample']
    diags = df['diagnosis']
    features = [col for col in df.columns.values if col not in ['sample', 'diagnosis']]
    x = StandardScaler().fit_transform(df[features])
    df_std = pd.DataFrame(x, columns=features)
    df_std['sample'] = samps
    df_std['diagnosis'] = diags
    df_std.set_index('sample', inplace=True)
    df_std.to_csv(output)
# end standardize_data() -----------------------------------------------------------------------------------------------------------------------------

# method outputs scree plot for dataset --------------------------------------------------------------------------------------------------------------
def plot_scree(df ,output, data_set):
    features = df.columns[1:-1]
    pca = PCA().fit(df[features])
    sns.lineplot(data = pca.explained_variance_ratio_)
    plt.title(data_set + ' Scree Plot')
    plt.xlabel('PC')
    plt.ylabel('Explaination of Variance')
    plt.savefig(output)
# end plot_scree() -----------------------------------------------------------------------------------------------------------------------------------

# method performs hierarchical clustering on dataset and outputs dendrogram --------------------------------------------------------------------------
def plot_dendrogram(df, output, data_set):
    label_list = list(df['diagnosis'])
    df.drop(['sample','diagnosis'], inplace=True, axis=1)
    X = df.values
    dendrogram = sch.dendrogram(sch.linkage(X, method='ward'), orientation='left', labels=label_list)
    plt.title(data_set + ' Dendrogram')
    plt.ylabel('Samples')
    plt.xlabel('Euclidean distances')
    plt.show()
# end plot_dendrogram() ------------------------------------------------------------------------------------------------------------------------------

# method plots a grouped bar chart of the abundances of gene families in each dataset ---------------------------------------------------------------- 
def plot_features(df,df2, output):
    # get gene families present in RNA and DNA datasets
    rna_attrs = list(df.columns[1:-1])
    dna_attrs = list(df2.columns[1:-1])
    # find unique gene families
    attrs = set(rna_attrs + dna_attrs)
    # get counts of number of samples with each gene family present
    rna_counts = df[df[rna_attrs] > 0].count().reset_index()
    dna_counts = df2[df2[dna_attrs] > 0].count().reset_index()
    rna_counts.columns = ['Gene Family', 'RNA Count']
    dna_counts.columns = ['Gene Family', 'DNA Count']
    # create dataframe with rows for each unique family
    merged = pd.DataFrame()
    merged['Gene Family'] = list(attrs)
    # join RNA and DNA counts on gene family names
    merged = pd.merge(merged, rna_counts,  on='Gene Family')
    merged = pd.merge(merged, dna_counts,  on='Gene Family')
    # fill missing data with 0
    merged.fillna(0, inplace=True)
    # plot bar chart
    merged.set_index('Gene Family')[['RNA Count', 'DNA Count']].plot(kind='bar', figsize=(14, 10))
    plt.title('Percentile Trimmed Gene Families Sample Occurrence')
    plt.xticks([])
    plt.ylabel('Counts')
    plt.savefig(output)
# end plot_features() ------------------------------------------------------------------------------------------------------------------------------

# method performs PCA on dataset, retaining 95% of it's variability and saving to file -------------------------------------------------------------
def do_PCA(df, output):
    samps = df['sample']
    df.set_index('sample', inplace=True)
    diags = df['diagnosis']
    pca = PCA(0.95)
    features = df.columns[:-1]
    pca.fit(df[features])
    df_pca = pca.transform(df[features])
    df_pca = pd.DataFrame(df_pca)
    df_pca.set_index(samps, inplace=True)
    df_pca['diagnosis'] = diags
    df_pca.to_csv(output)
    print(df_pca.shape)
# do_PCA() -----------------------------------------------------------------------------------------------------------------------------------------

# method ensures that dataframe is ready for use by classification methods -------------------------------------------------------------------------
def configure_df(df, data):
    # set samples as index
    df.set_index('sample', inplace=True)
    # make diagnosis last column
    df = df[[c for c in df if c not in ['diagnosis']] + ['diagnosis']]
    print(df.head())
    # pickle
    df.to_pickle(data[:-4] + '.pkl')
# end configure_df() --------------------------------------------------------------------------------------------------------------------------------

# *********************************************************************************************************************************
# Begin Script
# *********************************************************************************************************************************
# script args
parser = argparse.ArgumentParser(description='Test')
parser.add_argument('-d', '--data', type=str, required=True, help='Import data path')
parser.add_argument('-d2', '--data2', type=str, required=False, help='2nd Import data path')
parser.add_argument('-o', '--output', type=str, required=True, help='output file path')
parser.add_argument('-ds', '--data_set', type=str, required=False, default='', help='Dataset, either RNA or DNA')
parser.add_argument('-s', '--standardize', type=bool, required=False, help='save standardized version of dataset')
parser.add_argument('-ps', '--scree', type=bool, required=False, help='output scree plot for dataset')
parser.add_argument('-hc', '--cluster', type=bool, required=False, help='output dendrogram')
parser.add_argument('-f', '--features', type=bool, required=False, help='generate plot of feature distribution')
parser.add_argument('-pca', '--pca', type=bool, required=False, help='convert dataframe to PCA dataset')
parser.add_argument('-c', '--configure', type=bool, required=False, help='arrange df to work with classification methods')

args = parser.parse_args()
output = args.output
data = args.data
data2 = args.data2
data_set = 'Metatranscriptome' if args.data_set == 'RNA' else 'Metagenome'

df = pd.read_csv(data)

if args.standardize:
    standardize_data(df, output)

if args.scree:
    plot_scree(df, output, data_set)

if args.cluster:
    plot_dendrogram(df, output, data_set)

if args.features:
    df2 = pd.read_csv(data2)
    plot_features(df,df2,output)

if args.pca:
    do_PCA(df, output)

if args.configure:
    configure_df(df, data)