# Anthony Gray
# AS.410.734.81
# Metagenomics Final Project

# This script contains methods to convert the huge number of gene families in each dataset into manageable features

import os
import csv
import pickle
import argparse
import pandas as pd

# method produces counts for the presence of each gene family among the samples of a dataset ------------------------------------------------
def find_feature_distribution(df, files_path, output):
    features = {}
    # collect extracted files 
    file_list = os.listdir(files_path)
    i = 1
    for row in df.itertuples():
        sample = row[1]
        datatype = 'DNA' if row[2] == 'metagenomics' else 'RNA'
        sample_files = [file for file in file_list if file.startswith(sample) and datatype in file and 'total' in file]
        for file in sample_files:
            with open(files_path + file) as f:
                readCSV = csv.reader(f, delimiter = ',')
                for row in readCSV:
                    # add new features as they are found
                    if row[0] not in features:
                        features[row[0]] = 1
                    # increment the gene family when it is enountered again
                    else:
                        features[row[0]] += 1
        print(f'sample {i} read')
        i += 1
    print('Converting Dataframe...')
    final_df = pd.DataFrame.from_dict(features,columns=['count'], orient = 'index')
    print(final_df.shape)
    print('Writing Dataframe to file')
    final_df.to_csv(output)
# end find_feature_distribution() ------------------------------------------------------------------------------------------------------------

# method finds subset of gene families that are fount in 99% of samples ----------------------------------------------------------------------
def trim_feature_distribution(df, output):
    print(df.shape)
    cutoff = int(df['count'].quantile(0.99))
    trim_df = df[df['count'] > cutoff]
    abundant_attrs = trim_df['Unnamed: 0'].values
    print(len(abundant_attrs))
    with open(output, 'wb') as f:
        pickle.dump(abundant_attrs, f)
# end trim_feature_distribution() ------------------------------------------------------------------------------------------------------------

# method finds the difference in gene family presence between control and disease groups and selects those with greater differences ----------
def find_divergent_features(df_control, df_cd, output):
    df_control.columns = ['family', 'control_count']
    df_cd.columns = ['family', 'cd_count']
    df = pd.merge(df_control, df_cd, on='family')
    df['difference'] = df['cd_count'] - df['control_count']
    des = df.describe()
    std_dev = des.loc['std','difference']
    mean = des.loc['mean','difference']
    max_var = mean + std_dev*2
    min_var = mean - std_dev*3
    df = df[~df['difference'].between(min_var, max_var)]
    abundant_attrs = df['family'].values
    print(len(abundant_attrs))
    with open(output, 'wb') as f:
        pickle.dump(abundant_attrs, f)
# end find_divergent_features() --------------------------------------------------------------------------------------------------------------

# method chooses a fixed number of random control and disease samples and assembles the metadata for them ------------------------------------
def sample_DNA_data(df_control, df_cd, outfile):
    control_df = df_control.sample(187)
    cd_df = df_cd.sample(337)
    reduced_df = pd.concat([cd_df, control_df], ignore_index=True).sample(frac=1).reset_index(drop=True)
    reduced_df.columns = ['External_ID', 'data_type', 'diagnosis', 'url']
    reduced_df.to_csv(outfile, index=False)
# end sample_DNA_data() ----------------------------------------------------------------------------------------------------------------------


# *********************************************************************************************************************************
# Begin Script
# *********************************************************************************************************************************
# script args
parser = argparse.ArgumentParser(description='Test')
parser.add_argument('-d', '--data', type=str, required=True, help='Import data path')
parser.add_argument('-o', '--output', type=str, required=True, help='output file path')
parser.add_argument('-f', '--files_path', type=str, required=False, help='path to data files')
parser.add_argument('-t', '--trim_features', type=bool, required=False, help='trigger feature trimming')
parser.add_argument('-d2', '--other_data', type=str, required=False, help='additional datafile')
parser.add_argument('-s', '--sample', type=bool, required=False, help='sample DNA dataset to match size of RNA dataset')


args = parser.parse_args()
files_path = args.files_path
output = args.output
data = args.data
trim_features = args.trim_features
other_data = args.other_data
sample = args.sample

df = pd.read_csv(data)

if files_path:
    find_feature_distribution(df, files_path, output)

if trim_features:
    trim_feature_distribution(df, output)

if other_data and not sample:
    df2 = pd.read_csv(other_data)
    find_divergent_features(df, df2, output)
    
if sample:
    df = pd.read_csv(data, header=None)
    df2 = pd.read_csv(other_data, header=None)
    sample_DNA_data(df, df2, output)
