#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 16:07:43 2022

@author: mockingbird
"""

import pymongo

class Mongo_Config:
    
    def __init__(self):
        try:
            # connecion a mongo
            self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
            
            # creation de la base de donnée
            self.mydb = self.myclient["Projet_Gutenberg"]
            # self.mydb = self.myclient["test"]
            
            # creer les collecions [index, reverse_index]
            self.reverse_index_collection = self.mydb["reverse_index"]
            self.index_collection = self.mydb["index"]
           
            # créer un index dans l'ordre décroissant [index]
            self.index_word = self.index_collection.create_index([ ("word", -1) ])
            self.index_text = self.index_collection.create_index([ ("text", -1) ])
            self.index_word_text = self.index_collection.create_index([ ("text", -1), ("word", -1) ])
           
            # créer un index dans l'ordre décroissant [reverse_index]
            self.reverse_index_word = self.reverse_index_collection.create_index([ ("word", -1) ])
            self.reverse_index_text = self.reverse_index_collection.create_index([ ("text", -1) ])
            self.reverse_index_text_word_text = self.reverse_index_collection.create_index([ ("text", -1), ("word", -1) ])
        except:
            print("Connexion lost !")
        
    def resetAll(self): 
        self.index_collection.drop()
        self.reverse_index_collection.drop()
        self.__init__()
        print('All data reset !')