#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 12:47:55 2022

@author: mockingbird
"""

from nltk.stem.snowball import EnglishStemmer
from nltk import word_tokenize
import numpy as np
import mongo_config
import time

"""
Okapi BM25 (BM stands for Best Matching)
"""

class QueryRanking:
    
    def __init__(self):
        self.bdd = mongo_config.Mongo_Config()
        self.query = []


    def string2list(self, chaine):
        """
        Lit une chaine de caractère et renvoie les mots sous forme d'une liste
        """
        liste = word_tokenize(chaine) # retourne une liste de mots a partir d'une chaine
        return liste
    
    
    def mot2racine(self, mot):
        """
        extrait la racine d'un mot donnée en parametre
        """
        stemmer = EnglishStemmer() # initlailsation 
        racine = stemmer.stem(mot) # on recupere la racine des mots donné en parametre
        return racine
    
    
    def string2list_root(self, string):
        """
        Transforme une chaine de caractere en liste de racine
        """
        liste =  self.string2list(string) # découpage en mots
        listeStem = [] # liste contanant les racines
        for mot in liste:
            word_root = self.mot2racine(mot) # extraire la racine du mot
            listeStem.append(word_root) # ajout dans le dictionnaire
        return listeStem

    
    def finder_reverse(self, query):
        
        """
        recherche les documents ou les mots de la recheche apparaissent
        """
        try:
            results = self.bdd.reverse_index_collection.aggregate([
                { '$unwind': { 'path': '$text' } }, 
                { '$match': { 'word': {'$in': query} } },
                { '$project': { '_id': 0, 'word': 0} },
                { '$sort': { 'tf_idf': 1 } }
            ])
        except:
            print("error on search !")
        return list(results)
   
    
    def count_docs(self):
        """
        caclul le nombre de documents
        """
        try:
            count_index = self.bdd.index_collection.aggregate([
                { '$group': { '_id': 'null', 'myCount': { '$sum': 1 } } },
                { '$project': { '_id': 0 } }
            ])
            for count in count_index:
                return count["myCount"]
        except:
            print("error on search !")
            
            
    def count_words(self):
        """
        caclul le nombre de mots present au total
        """
        count_index = self.bdd.reverse_index_collection.aggregate([
            { '$group': { '_id': 'null', 'myCount': { '$sum': 1 } } },
            { '$project': { '_id': 0 } }
        ])
        for count in count_index:
            return count["myCount"]
        
    def find_all_reverse(self):
        """
        retourne tous les resultats de la base
        """
        try:
            result = self.bdd.reverse_index_collection.find({}, {"_id": 0})
        except:
            print("error on find !")
        return result

    def bm25_idf(self, results):
       """
       calculer IDF pour les fichiers resultats
       """
       scored_results = {}
       for doc in results:
           df = doc['df']
           idf = doc['text']['tf'] * np.log10((self.count_docs() - df + 0.5) / (df + 0.5) +1)
           scored_results[doc['text']['name']] =  idf
       return scored_results
       
    
    def sort_ranked(self, scored_results):
        """
        trier les resultats obtenus selon leurs score
        """
        liste = []
        results = {k: v for k, v in sorted(scored_results.items(), key=lambda item: item[1], reverse=True)}
        for e in results:
            liste.append({'file_title': e})
        return liste
    
    
    def start(self, string):
        """
        fait la recherche -> calcul IDF -> trie les resultats et calcule le temps de toute l'opération [ main() ]
        """
        t_start = time.time_ns()
        list_query = self.string2list_root(string)
        reverse = self.finder_reverse(list_query)
        results = self.bm25_idf(reverse)
        sorted_10_results = self.sort_ranked(results) 
        t_end = (time.time_ns() - t_start)/1000000000
        return sorted_10_results[0: 10], t_end
    
# if __name__ == '__main__':
#     print(QueryRanking().start())