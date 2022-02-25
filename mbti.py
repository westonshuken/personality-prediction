import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import seaborn as sns
import re
import pickle

from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer



from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import plot_confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score

from imblearn.under_sampling import RandomUnderSampler

class preprocess:

    def url_remove(self, post):
        return re.sub(r'http\S+', '', post)

    def pipe_remove(self, post):
        return re.sub(r'[|]', ' ', post)

    def punc_remove(self, post):
        return re.sub(r'[\'_:]', '', post)

    def remove_dig_token(self, post):
        return [post[i] for i in range(len(post)) if post[i].isalpha()]

    def remove_stopwords(self, post):
        sw = stopwords.words('english')
        return [post[i] for i in range(len(post)) if post[i] not in sw]


class run_models:
    '''
    '''
    def run(self, df, X_column, targets, models, table, tfidf=False, SEED=234819381):
        '''
        '''
        for target in targets:
            print('-'*20)

            X = df[X_column]
            y = df[target]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=SEED)

            if tfidf == True:
                print(f'Vectorizing....  @ {time.asctime()}')
                vc = TfidfVectorizer(ngram_range=(1,2))
                X_train_vc = vc.fit_transform(X_train)
                X_test_vc = vc.transform(X_test)
                
            else:
                print(f'Vectorizing....  @ {time.asctime()}')
                vc = CountVectorizer(ngram_range=(1,2))
                X_train_vc = vc.fit_transform(X_train)
                X_test_vc = vc.transform(X_test)

            for clf in models:  
            
                model_name = str(clf)
                print(f'Working on {model_name} for {target} @ {time.asctime()}')

                models[clf].fit(X_train_vc, y_train)
                cv_score = cross_val_score(models[clf], X_train_vc, y_train, cv=5)
                cv_score_mean = round(np.mean(cv_score), 4)
            
                y_pred = models[clf].predict(X_test_vc)
                acc_score = accuracy_score(y_pred, y_test)

                table = table.append({'Model': model_name + "_" + target, 'Target': target, 'CVScore': round(cv_score_mean, 4), \
                                                    'TestAcc': round(acc_score, 4)}, ignore_index=True)

        return table


    def run_usampled(self, df, X_column, targets, models, table, tfidf=False, SEED=234819381):
        '''
        '''
        for target in targets:
            train_set, test_set = train_test_split(df, random_state=SEED)

            X_train = train_set[X_column]
            X_train = np.array(X_train).reshape(-1, 1)

            y_train = train_set[target]
            y_train = np.array(y_train).reshape(-1, 1)

            # instantiating the random undersampler
            rus = RandomUnderSampler() 

            # resampling training set X & y
            X_rus, y_rus = rus.fit_resample(X_train, y_train)

            # new class distribution
            print(np.unique(y_train, return_counts=True))
            print(np.unique(y_rus, return_counts=True))

            X_rus = pd.Series(X_rus.reshape(-1))
            y_rus = pd.Series(y_rus.reshape(-1))

            if tfidf == True:
                print(f'Vectorizing....  @ {time.asctime()}')
                vc = TfidfVectorizer(ngram_range=(1,2))
                X_train_vc = vc.fit_transform(X_rus)
                X_test_vc = vc.transform(test_set[X_column])
                
            else:
                print(f'Vectorizing....  @ {time.asctime()}')
                vc = CountVectorizer(ngram_range=(1,2))
                X_train_vc = vc.fit_transform(X_rus)
                X_test_vc = vc.transform(test_set[X_column])

            for clf in models:  
                
                model_name = str(clf)
                print(f'Working on {model_name} @ {time.asctime()}')

                models[clf].fit(X_train_vc, y_rus)

                cv_score = cross_val_score(models[clf], X_train_vc, y_rus, cv=5)
                cv_score_mean = round(np.mean(cv_score), 4)

                y_pred = models[clf].predict(X_test_vc)
                acc_score = accuracy_score(y_pred, test_set[target])

                table = table.append({'Model': model_name + "_" + target, 'Target': target, 'CVScore': round(cv_score_mean, 4), \
                                                    'TestAcc': round(acc_score, 4)}, ignore_index=True)

        return table