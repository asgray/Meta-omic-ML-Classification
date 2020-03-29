import os
import time
import pickle
import argparse
import requests
import pandas as pd
from tqdm import tqdm
from playsound import playsound
import concurrent.futures as cf

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Protein_Family:
    def __init__(self, ID):
        self.ID = ID
        self.in_DNA_diff = False
        self.in_RNA_diff = False
        self.in_DNA_filter = False
        self.in_RNA_filter = False
        self.in_all = False
        self.UniRef_URL = None
        self.UniRef_result = None

    def __repr__(self):
        rep = (
            f'{self.ID}\nDNA Δ: {self.in_DNA_diff} DNA %: {self.in_DNA_filter} '
            f'\nRNA Δ: {self.in_RNA_diff} RNA %: {self.in_RNA_filter} \nIn all sets: '
            f'{self.in_all}\nURL: {self.UniRef_URL}\n'
            f'{self.UniRef_result}\n'
        )
        return rep

    def __eq__(self, other):
        if self.ID == other.ID: return True 
        return False
# end Protein Family class -------------------------------------------------------------------------------------------------------------------------------------------------

#
def build_sets(data_path, destination):
    # find all dataframes in directory
    feature_sets = os.listdir(data_path)
    data = {}
    combined_features = set()
    
    # create dictionary of filename: feature list
    for s in feature_sets:
        # import data file
        with open(data_path + s, 'rb') as f:
            data[s] = pickle.load(f)
    
    # form set of all protein families
    for d in data:
        for f in data[d]:
            combined_features.add(f)
    combined_features.remove('diagnosis')

    # create objects holding 
    prot_families = []
    for family in combined_features:
        fam_obj = Protein_Family(family)
        if fam_obj.ID in data['DNA_diff_feats.pkl']: fam_obj.in_DNA_diff = True
        if fam_obj.ID in data['DNA_filter_feats.pkl']: fam_obj.in_DNA_filter = True
        if fam_obj.ID in data['RNA_diff_feats.pkl']: fam_obj.in_RNA_diff = True
        if fam_obj.ID in data['RNA_filter_feats.pkl']: fam_obj.in_RNA_filter = True
        if fam_obj.in_DNA_diff and fam_obj.in_DNA_filter and fam_obj.in_RNA_diff and fam_obj.in_RNA_diff and fam_obj.in_RNA_filter:
            fam_obj.in_all = True
        prot_families.append(fam_obj)

    pickle.dump(data, open(destination + 'features.pkl', 'wb'))
    pickle.dump(prot_families, open(destination + 'protein_families.pkl', 'wb'))
# end build_sets() --------------------------------------------------------------------------------------------------------------------------------------

#
def get_urls(fam):#, destination):
    cluster = fam.ID.split('_')[1]  # extract cluster name
    url = f'https://www.uniprot.org/uniprot/?query=accession:{cluster}&format=tab'         
    if fam.UniRef_URL is None:  # only try if the previous ones did not work
        try:
            res = requests.head(url)
            # save URL if it works
            if res.status_code == 200:
                print(cluster + ' works')
                fam.UniRef_URL = url
            else:
                print(url + ' bad url')
        except:
            print('Something went wrong')
# end get_urls() ------------------------------------------------------------------------------------------------------------------------------------------

#
def download_data(fam):
    if fam.UniRef_result is None:
        # try to download if not done yet
        try:
            res = requests.get(fam.UniRef_URL)
            rows = res.text.split('\n')
            tab = [row.split('\t') for row in rows]
            df = pd.DataFrame(tab[1:],columns=tab[0])
            # add to family object
            fam.UniRef_result = df
            # print(f'{fam.ID} data downloaded')
        except:
            print('Something went wrong')
# end download_data() -------------------------------------------------------------------------------------------------------------------------------------

# script args
parser = argparse.ArgumentParser(description='Test')
parser.add_argument('-o', '--output', type=str, required=True, help='Output Destination')
parser.add_argument('-d', '--data', type=str, required=True, help='Import dataset path')
parser.add_argument('-save', '--save', type=str, required=False, help='pickle output file')
parser.add_argument('-c', '--columns', type=str, required=False, help='Extract dataset column names')
parser.add_argument('-set', '--sets', type=str, required=False, help='Organize protein falmilies')
parser.add_argument('-url', '--url', type=str, required=False, help='find and store UniRef urls for each family')
parser.add_argument('-dl', '--download', type=str, required=False, help='download UniProt data based on found url')

args = parser.parse_args()
data_path = args.data
destination = args.output

data = None
# import data file
with open(data_path, 'rb') as f:
    data = pickle.load(f)

# data = data[:5]

# extract features from a dataframe
if args.columns:
    features = data.columns
    pickle.dump(features, open(destination, 'wb'))

if args.sets:
    build_sets(data_path, destination)

if args.url:
    with cf.ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(get_urls, data), total = len(data)))

if args.download:
    with cf.ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(download_data, data), total = len(data)))

yes, no = 0,0
shapes = set()
for fam in data:
    shapes.add(fam.UniRef_result.shape)

print(yes,no)
for shape in shapes:
    for fam in data:
        if fam.UniRef_result.shape == shape:
            print(shape)
            print(fam)
            break
if args.save:
    pickle.dump(data, open(destination + 'fam_urls.pkl', 'wb'))

playsound('ping.wav')