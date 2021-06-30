# Anthony Gray
# AS.410.734.81
# Metagenomics Final Project

# This script uses the metadata file from the IBDMDB website to download and organize the associated data

import os
import csv
import wget
import pickle
import tarfile
import argparse
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from playsound import playsound
import concurrent.futures as cf

# Method checks which of several urls on the IBDMDB site works for each sample set -----------------------------------
def test_urls(row):
    # retrieve sample accession
    sample = row['External_ID']
    data_type = row['data_type']
    filename =  sample + '_humann2.tar.bz2'
    # each URL base links to a different project section on the site
    url1 = 'https://ibdmdb.org/tunnel/products/HMP2/WGS/1818/' + filename
    url2 = 'https://ibdmdb.org/tunnel/products/SwedishTwins/WGS/1441/' + filename
    url3 = 'https://ibdmdb.org/tunnel/products/HMP2_Pilot/WGS/1644/' + filename
    url4 = 'https://ibdmdb.org/tunnel/products/HMP2_Pilot/MTX/1524/' + filename
    url5 = 'https://ibdmdb.org/tunnel/products/HMP2/MTX/1750/' + filename
    # duplicate IDs require the right data download
    genome_urls = [url1, url2, url3]
    trancript_urls = [url4, url5]
    urls = genome_urls if data_type == 'metagenomics' else trancript_urls
    # test if each url is good, return the one that works
    for url in urls:
        # test if each url is good, return the one that works
        res = requests.head(url)
        if res.status_code == 200:
            print(url + ' works')
            return url
        else:
            print(filename + ' bad url')
# end test_urls() ----------------------------------------------------------------------------------------------------

# Method uses test_urls() to fill in URL for each sample in the metadata spreadsheet ---------------------------------
def assign_urls(df):
    df['url'] = None
    df['url'] = df.apply(test_urls, axis=1)
# end assign_urls() --------------------------------------------------------------------------------------------------

# Method downloads Tarfile for each sample based on the URLS filled into the metadata spreadsheet --------------------
def download_samples(df, destination):
    # test if file has already been downloaded
    already_downloaded = os.listdir(destination)
    i = 1
    for row in df.itertuples():
        url = row[4]
        sample = row[1]
        data_type = row[2]
        dt = 'DNA' if data_type == 'metagenomics' else 'RNA'
        file_name = sample + '_' + dt + '_' + 'humann2.tar.bz2'
        file_path = destination + file_name
        # download samples via associated URL
        if file_name not in already_downloaded:
            try:
                print('Downloading ' + file_name)
                wget.download(url, file_path)
                print(f'\n sample {i} downloaded successfully \n')
            except Exception as e:
                print('\n' + file_name + ' could not be downloaded: ' + str(e) + '\n')
        else:
            print(file_name + ' already downloaded')
        i += 1
# end download_samples() ----------------------------------------------------------------------------------------------

# Mehod retrieves gene family composition file from tarfile, saves total composition and composition by taxa in separate files
def extract_gene_families(df, destination):
    # make new directory
    genefamilies_folder = destination + 'GeneFamilies'
    # check extracted files that already exist 
    already_extracted_dna = os.listdir(genefamilies_folder + '/DNA')
    already_extracted_rna = os.listdir(genefamilies_folder + '/RNA')
    already_extracted = already_extracted_dna + already_extracted_rna
    for row in df.itertuples():
        sample = row[1]
        data_type = row[2]
        dt = 'DNA' if data_type == 'metagenomics' else 'RNA'
        tarfile_name = sample + '_' + dt + '_humann2.tar.bz2'
        print(tarfile_name)
        genefamilies_filename = sample + '_genefamilies.tsv'
        if sample + '_total.csv' not in already_extracted:
            print('Extracting gene families from ' + tarfile_name)
            try:
                # extract gene family file
                tar = tarfile.open(Path(destination + tarfile_name), 'r:bz2') 
                f = tar.extractfile(genefamilies_filename)
                content = f.readlines()
                # save each line in one of two lists
                total_families = []
                families_by_tax = []
                for line in content:
                    line = line.decode().strip()
                    # '#' is the header line
                    if '|' not in line and '#' not in line:
                        line = line.split('\t')
                        total_families.append(line)
                    # '|' is used to separate the gene family and taxonomy information
                    elif '|' in line and '#' not in line:
                        line = line.split('\t')
                        families_by_tax.append(line)
                    else:
                        pass
                # make dataframe of each list of lines
                total_df = pd.DataFrame(total_families)
                tax_df = pd.DataFrame(families_by_tax)
                # save dataframes as CSVs
                total_df.to_csv(genefamilies_folder + '/'+dt+'/' + sample + '_' + dt + '_total.csv', index=False, header=False)
                tax_df.to_csv(genefamilies_folder + '/'+dt+'/' + sample + '_' + dt +'_by_taxa.csv', index=False, header=False)
            except Exception as e:
                print(tarfile_name + ' could not be extracted: ' + str(e) + '\n')
        else:
            print('Gene families already extracted from ' + tarfile_name)
# end extract_gene_families() -----------------------------------------------------------------------------------------------------

# Method uses metadata file, selected attribute file, and gene family files to build a dataset ------------------------------------
# each sample is a row, each gene family is a column
def collate_datasets(df, destination, files_path, set_flag, pickle_file):
    # retrieve list of selected attributes
    with open(pickle_file, 'rb') as f:
        attrs = pickle.load(f)
    # parse flag string to get data type and subset
    data_type = set_flag[:3].upper()
    attribute_type = set_flag[-3:]

    print(data_type, attribute_type)
    out_file_name = set_flag + '_df.csv'
    instances = []
    # collect extracted files 
    file_list = os.listdir(files_path)
    i = 1
    for row in df.itertuples():
        # extract metadata
        sample, sample_type, diagnosis = row[1], row[2], row[3]
        # only choose targeted metadata 
        if (sample_type == 'metagenomics' and data_type == 'DNA') or (sample_type == 'metatranscriptomics' and data_type == 'RNA'):
            print('Adding ' + sample)
            # retreive list of files associated with sample
            sample_files = [file for file in file_list if file.startswith(sample) and data_type in file and attribute_type in file]

            for file in sample_files:
                # build dictionary of sample attributes
                instance = {'sample': sample, 'diagnosis': diagnosis}
                with open(files_path + file) as f:
                    readCSV = csv.reader(f, delimiter = ',')
                    for row in readCSV:
                            attr = row[0]
                            if attr in attrs:
                                val = float(row[1])
                                # round extremely small values down to 0
                                instance[attr] = val if val >= 0.00001 else 0.0
                instances.append(instance)
            print(f'sample {i} added successfully')
            i += 1
    # convert list of dictionaries to dataframe, fill missing values with 0
    print('Converting Dataframe...')
    final_df = pd.DataFrame.from_dict(instances)
    final_df = final_df.fillna(0.0)
    # move diagnosis to last column
    cols = list(final_df.columns)
    cols = cols[-1:] + cols[:-1]
    final_df = final_df[cols]
    print(final_df.shape)

    # remove columns with one value
    nunique = final_df.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique == 1].index
    final_df = final_df.drop(cols_to_drop, axis=1)
    # print(final_df)
    print('Writing Dataframe to file')
    # save as data file
    final_df.to_csv(destination + out_file_name, index=False)
# end collate_datasets() ----------------------------------------------------------------------------------------------------------

# *********************************************************************************************************************************
# Begin Script
# *********************************************************************************************************************************
# script args
parser = argparse.ArgumentParser(description='Test')
parser.add_argument('-o', '--output_folder', type=str, required=True, help='Output Destination')
parser.add_argument('-d', '--data', type=str, required=True, help='Import dataset path')
parser.add_argument('-u', '--url', type=bool, required=False, help='Option for url management')
parser.add_argument('-g', '--get', type=bool, required=False, help='Option to download data')
parser.add_argument('-s', '--save', type=bool, required=False, help='Option to save dataset with urls')
parser.add_argument('-e', '--extract', type=bool, required=False, help='Option to extract files from tarfiles')
parser.add_argument('-f', '--files', type=str, required=False, help='Path to sample files')
parser.add_argument('-x', '--set_flag', type=str, required=False, help='Flag to indicate which type of data to collate: dna_tax, dna_tot, rna_tax, rna_tot')
parser.add_argument('-p', '--pickle_file', type=str, required=False, help='path to pickled attribute list')

args = parser.parse_args()
data_path = args.data
destination = args.output_folder
# windows path parsing adds '"' to argument, need to trim to use filepath string
# FIX ME ********************************************
if args.extract:
    destination = destination[:-1] + '\\'
# DON'T KNOW WHY THIS IS NEEDED
# ***************************************************
files_path = args.files
pickle_file = args.pickle_file

# prevent invalid flags
set_flag = args.set_flag
possible_set_flags = ['dna_tax', 'dna_tot', 'rna_tax', 'rna_tot']
if set_flag and set_flag not in possible_set_flags:
    print('Possible set flags are: gen_tax, gen_tot, tran_tax, tran_tot')
    quit()

# import metadata file
df = pd.read_csv(data_path, header=None)

# run methods based on arg flags
if args.url:
    assign_urls(df)

if args.save:
    print('Saving dataset with URLs')
    df.to_csv(data_path[:-4] + '_url.csv', index = False)

if args.get:
    download_samples(df, destination)

if args.extract:
    extract_gene_families(df, destination)

if args.files:
    collate_datasets(df, destination, files_path, set_flag, pickle_file)