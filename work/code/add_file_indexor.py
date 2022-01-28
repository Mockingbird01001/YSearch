#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 21:00:33 2022

@author: mockingbird
"""

from itertools import filterfalse
from os import listdir
import index_reverse

class Add_file_indexor:
    
    def __init__(self):
        self.index = index_reverse.Indexeur_inverse()
        self.NBDOCS = len(listdir(self.index.outils.DOSSIERDOCUMENTS)) # nombre de document dans le HDFS
        # identifie les nouveau fichiers ajouté   
        self.new_files = list(filterfalse(self.index.outils.loadFile2List("old_file.txt").__contains__, listdir(self.index.outils.DOSSIERDOCUMENTS)))
        
    def docs2dicoDoc(self):
        """
        traitement des fichiers contenus dans DOSSIERDOCUMENTS et convertit le corpus en dico doc -> stem -> fréq
        """
        dicoDocs = {} # initialisation du dictionnaire
        loadedFile_liste = [] # initalisation de la liste des nouveau fichiers indexé
        # parcours des fichiers du répertoire DOSSIERDOCUMENT, à l'aide de la focntion listdir du module os
        for filename in self.new_files:
            loadedFile_liste.append(filename)
            print(filename)
            try:
                filecontent = self.index.outils.loadFile_UTF8(filename) # ouverture du fichier en UTF-8 - sig with BOW (bag-of-words)
            except:
                filecontent = self.index.outils.loadFile_ISO(filename) # ouverture du fichier en ISO 8859-1
            listeMots =  self.index.outils.string2list(filecontent) # découpage en mots
            liste = self.index.filter_general(listeMots) # filtrage
            listeStem = [] # liste contanant les racines
            for mot in liste:
                word_root = self.index.outils.mot2racine(mot) # extraire la racine du mot
                listeStem.append(word_root)
            listeStem = self.index.filter_general(listeStem) # filtrage
            dicoDocs[filename] = self.index.outils.liste2dico(listeStem) #construction du dictionnaire mot --> fréquence et ajout dans dico final
        self.index.outils.list2file(loadedFile_liste, "old_file.txt")
        return dicoDocs
    
    
    def reverse_index(self):
        index = self.docs2dicoDoc() # preparation de l'index et calcul du TF
        indexDF = self.index.calculeDFdico(index) # ajouter les DF pour chque fichier
        reversIndex = self.index.dicoDoc2dicoStem(indexDF) # preparation de l'index inversé
        reversIndexDF = self.index.calculeDFdico(reversIndex) # calcul le total "df"
        reversIndexTF = self.index.calculenormalizedTFdico(reversIndexDF) # calcul le TF * IDF normalisé dans le fichier
        return index, reversIndexTF