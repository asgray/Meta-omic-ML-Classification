<<<<<<< HEAD
# Anthony Gray
# AS.410.734.81
# Metagenomics Final Project

# This script uses pickled datasets and classification models to assess the classificability of a dataset

import os
import pickle
import argparse
import pandas as pd
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Both methods use the passed model to assign a classification to a dataframe in the Guess column ----------------------------------
# works for NB, SVC, KNN
def get_predictions(model, train, test):
    mod = model()
    pred = mod.fit(train.drop('diagnosis', axis=1), train['diagnosis']).predict(test.drop('diagnosis', axis=1))
    test.loc[:,'guess'] = pred

# RF has a single parameter
def get_RF(model, train, test):
    clf = model(n_jobs=2)
    pred = clf.fit(train.drop('diagnosis', axis=1), train['diagnosis']).predict(test.drop('diagnosis', axis=1))
    test.loc[:,'guess'] = pred
# end get_predictions() and get_RF() ----------------------------------------------------------------------------------------------

# Method compares the Guessed class to the acutal class and outputs the accuracy of the classification ----------------------------
def calc_accuracy(df):
    df_sub = df[['diagnosis','guess']]
    correct= df_sub['diagnosis'].eq(df_sub['guess'])
    cts = correct.value_counts().loc[True]
    return cts/correct.shape[0]
# end calc_accuracy() -------------------------------------------------------------------------------------------------------------


# *********************************************************************************************************************************
# Begin Script
# *********************************************************************************************************************************
# script args
parser = argparse.ArgumentParser(description='Classifier Methods')
parser.add_argument('-d', '--data', type=str, required=True, help='Import dataset path')
parser.add_argument('-m', '--model', type=str, required=True, help='specify model to be used')
args = parser.parse_args()

df = pd.read_pickle(args.data)

# assign model and classifier method based on input
model = args.model
runmodel = get_predictions
if model == 'SVC':
    model = SVC

elif model == 'NB':
    model = GaussianNB
    
elif model == 'KNN':
    model = KNeighborsClassifier

elif model == 'RF':
    model = RandomForestClassifier
    runmodel = get_RF
else:
    print('Model must be SVC, NB, KNN or RF')
    quit()

acc = []
for i in range(5):
    # random stratified train/test split
    train, test = train_test_split(df, test_size=0.2, stratify=df['diagnosis'])
    # perform classification
    runmodel(model, train, test)
    # save classification value
    acc.append(round(calc_accuracy(test),4)*100)
    
# output classifciation accuracies and thier average
print(f'Observations: {acc} \nAverage: {round(sum(acc)/len(acc),4)}')







# def split_data(df, output, re_split):
    # if re_split:
    #     train, test = train_test_split(df, test_size=0.2, random_state=0, stratify=df['diagnosis'])
    #     with open(output, 'wb') as f:
    #         pickle.dump([train, test], f)
    # else:
    #     file_list = os.listdir('.')
    #     if output in file_list:
    #         with open(output, 'rb') as f:
    #             data = pickle.load(f)
    #         train, test = data[0], data[1]
=======
# Anthony Gray
# AS.410.734.81
# Metagenomics Final Project

# This script uses pickled datasets and classification models to assess the classificability of a dataset

import os
import pickle
import argparse
import pandas as pd
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Both methods use the passed model to assign a classification to a dataframe in the Guess column ----------------------------------
# works for NB, SVC, KNN
def get_predictions(model, train, test):
    mod = model()
    pred = mod.fit(train.drop('diagnosis', axis=1), train['diagnosis']).predict(test.drop('diagnosis', axis=1))
    test.loc[:,'guess'] = pred

# RF has a single parameter
def get_RF(model, train, test):
    clf = model(n_jobs=2)
    pred = clf.fit(train.drop('diagnosis', axis=1), train['diagnosis']).predict(test.drop('diagnosis', axis=1))
    test.loc[:,'guess'] = pred
# end get_predictions() and get_RF() ----------------------------------------------------------------------------------------------

# Method compares the Guessed class to the acutal class and outputs the accuracy of the classification ----------------------------
def calc_accuracy(df):
    df_sub = df[['diagnosis','guess']]
    correct= df_sub['diagnosis'].eq(df_sub['guess'])
    cts = correct.value_counts().loc[True]
    return cts/correct.shape[0]
# end calc_accuracy() -------------------------------------------------------------------------------------------------------------


# *********************************************************************************************************************************
# Begin Script
# *********************************************************************************************************************************
# script args
parser = argparse.ArgumentParser(description='Classifier Methods')
parser.add_argument('-d', '--data', type=str, required=True, help='Import dataset path')
parser.add_argument('-m', '--model', type=str, required=True, help='specify model to be used')
args = parser.parse_args()

df = pd.read_pickle(args.data)

# assign model and classifier method based on input
model = args.model
runmodel = get_predictions
if model == 'SVC':
    model = SVC

elif model == 'NB':
    model = GaussianNB
    
elif model == 'KNN':
    model = KNeighborsClassifier

elif model == 'RF':
    model = RandomForestClassifier
    runmodel = get_RF
else:
    print('Model must be SVC, NB, KNN or RF')
    quit()

acc = []
for i in range(5):
    # random stratified train/test split
    train, test = train_test_split(df, test_size=0.2, stratify=df['diagnosis'])
    # perform classification
    runmodel(model, train, test)
    # save classification value
    acc.append(round(calc_accuracy(test),4)*100)
    
# output classifciation accuracies and thier average
print(f'Observations: {acc} \nAverage: {round(sum(acc)/len(acc),4)}')







# def split_data(df, output, re_split):
    # if re_split:
    #     train, test = train_test_split(df, test_size=0.2, random_state=0, stratify=df['diagnosis'])
    #     with open(output, 'wb') as f:
    #         pickle.dump([train, test], f)
    # else:
    #     file_list = os.listdir('.')
    #     if output in file_list:
    #         with open(output, 'rb') as f:
    #             data = pickle.load(f)
    #         train, test = data[0], data[1]
>>>>>>> d11fed841e9ab9caa986f2a85b287800468216d2
    # return train, test