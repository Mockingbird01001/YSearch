#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nltk.stem.snowball import EnglishStemmer
from nltk import word_tokenize

from string import ascii_lowercase
from codecs import open

import re

class Outils:
    
    def __init__(self):
        # self.DOSSIERDOCUMENTS = "/home/ysearch/work/data/"
        self.DOSSIERDOCUMENTS = "../data/"
        self.stopWords = "stopwords.txt"
        self.MOTSOUTILS = self.loadFile2List(self.stopWords)
    

    def loadFile_UTF8(self, filename):
        """
        Lit un fichier et le renvoie sous forme de chaine encodé (tout en minuscule)
        """
        with open(self.DOSSIERDOCUMENTS + filename, encoding='utf-8-sig') as file:
            return file.read().lower()
        
        
    def loadFile_ISO(self, filename):
        """
        Lit un fichier et le renvoie sous forme de chaine encodé (tout en minuscule)
        """
        with open(self.DOSSIERDOCUMENTS + filename, encoding='ISO-8859-1') as file:
            return file.read().lower()
    
    
    def loadFile2List(self, filename):
        """
        Lit un fichier et le renvoie les mots sous forme d'une liste (tout en minuscule)
        """
        list_oublie = []
        with open(filename, encoding='utf-8') as f:
            for line in f:
                list_oublie.append(line.replace('\n', '').lower())
        return self.tokenize_plus(list_oublie)
    
    
    def string2list(self, chaine):
        """
        Lit une chaine de caractère et renvoie les mots sous forme d'une liste
        """
        return word_tokenize(chaine)


    def tokenize_plus(self, listetokens):
        """
        Traite les chaines non tokenizées avec apostrophe
        """
        for token in listetokens:
            if ("'" in token):
                listetokens.remove(token)
                listetokens += token.split("'")
            if ("’" in token):
                listetokens.remove(token)
                listetokens += token.split("’")
            if ("/" in token):
                listetokens.remove(token)
                listetokens += token.split("/")
        return listetokens

        
    def nettoieMot(self, mot):
        """
        Enlève les caractères spéciaux
        """
        i=0
        for c in mot:
            if c in u"«»ł.├_-—":
                mot = mot[:i]+mot[i+1:]
        return mot
    
    
    def removeHexa(self, mot):
        return re.sub(r'[^\x00-\x7f]',r'', mot)
            
    
    def contientLettres(self, chaine):
        for c in chaine:
            if c in ascii_lowercase:
                return True
        return False
    
    
    def liste2dico(self, liste):
        """
        Lit une liste de racines et renvoie le dictionnaire correspondant (mot -> fréquence)
        """
        dico = {} #initialisation du nouveau dictionnaire
        for mot in liste: # parcours des mots de la liste
            if mot in dico.keys(): # si le mot est déjà une clé du dictionnaire on incrémente sa fréquence
                dico[mot] += 1
            else: # sinon on l'ajoute comme nouvelle clé
                dico[mot] = 1
        return dico
    
    
    def list2file(self, file_liste, nameFile):
        """
        stocke dans un fichier la liste des fichier indexé
        """
        textfile = open(nameFile, "r+")
        for element in file_liste:
            new = element + "\n"
            textfile.write(new)
        textfile.close()
    
    
    def mot2racine(self, mot):
        """
        retourne la racine d'un mot donné en parametre
        """
        stemmer = EnglishStemmer()
        racine = stemmer.stem(mot)
        return racine