#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 21:21:48 2022

@author: mockingbird
"""

from math import log10
from os import listdir
import outils

"""
Okapi BM25 (BM stands for Best Matching)
"""

class Indexeur_inverse:
   
    def __init__(self):
        self.outils = outils.Outils() # import de la librairie outils
        self.NBDOCS = len(listdir(self.outils.DOSSIERDOCUMENTS)) # nombre de document dans le HDFS
        
    def filter_general(self, listeMots):
        """
        Prend une liste de tokens en entrée et renvoie une liste filtré en sortie
        """
        listeResultat = [] # liste dans laquelle on va recopier les mots
        for mot in listeMots:
            # supprime les éléments qui ne sont pas des mots (ponctuation etc.)
            if self.outils.contientLettres(mot): #on garde tout ce qui contient une lettre
                # Prend en entrée une liste de mots et en retire les caracteres speciaux
                mot_nettoye = self.outils.nettoieMot(mot)
                # Prend en entrée une liste de mots et en filtre les mots outils   
                
                if mot_nettoye not in self.outils.MOTSOUTILS: # on garde tout ce qui n'est pas un mot outil
                    listeResultat.append(self.outils.removeHexa(mot_nettoye))
        return listeResultat

    def docs2dicoDoc(self):
        """
        traitement des fichiers contenus dans DOSSIERDOCUMENTS et convertit le corpus en dico doc -> stem -> fréq
        """
        dicoDocs = {} # initialisation du dictionnaire
        loadedFile_liste = []
        # parcours des fichiers du répertoire DOSSIERDOCUMENT, à l'aide de la focntion listdir du module os
        for filename in listdir(self.outils.DOSSIERDOCUMENTS):
            loadedFile_liste.append(filename)
            try:
                filecontent = self.outils.loadFile_UTF8(filename) # ouverture du fichier en UTF-8 - sig with BOW (bag-of-words)
            except:
                filecontent = self.outils.loadFile_ISO(filename) # ouverture du fichier en ISO 8859-1
            listeMots =  self.outils.string2list(filecontent) # découpage en mots
            liste = self.filter_general(listeMots) # filtrage
            listeStem = [] # liste contanant les racines
            for mot in liste:
                word_root = self.outils.mot2racine(mot) # extraire la racine du mot
                listeStem.append(word_root)
            listeStem = self.filter_general(listeStem) # filtrage
            dicoDocs[filename] = self.outils.liste2dico(listeStem) #construction du dictionnaire mot --> fréquence et ajout dans dico final
            self.outils.list2file(loadedFile_liste, "old_file.txt")
        return dicoDocs
    
    
    def dicoDoc2dicoStem(self, dicoDoc):
        """
        prend en entrée la sortie de docs2dicoDoc (dico doc -> stem -> fréq) et le transforme en fichier inverse : stem -> doc -> freq
        """
        dicoStem = {} # initialisation du dictionnaire
        for (file, dicoFile) in dicoDoc.items(): # parcours des documents
            for stem in dicoFile: # parcours des racines
                if stem != 'df':
                    if stem in dicoStem.keys():
                        #si le stem st déjà dans le dico résultat on ajoute sa fréquence pour le document file
                        dicoStem[stem][file] = dicoFile[stem]
                    else:
                        # sinon on crée un nouveau dictionnaire qu'on ajoute pour ce stem, puis on ajoute au dictionnaire le doc et la fréquence
                        dicoStem[stem] = {}
                        dicoStem[stem][file] = dicoFile[stem]
        return dicoStem
    
    
    def calculeDFdico(self, dicoStem):
        """
        prend en entrée le dico stem et calcule le DF de chaque stem et le stocke dans le dico à l'indice "df"
        """
        for stem in dicoStem:
            dicoStem[stem]["df"] = len(dicoStem[stem])
        return dicoStem
    
    
    def calculenormalizedTFdico(self, dicoStem, k=1.25, b=0.75):
        """
        calcule le tf normalisé de chaque stem/doc
        """
        try:
            avg_d_len = sum(dicoStem[stem][doc] for stem in dicoStem for doc in dicoStem[stem]) / self.NBDOCS
        except:
            avg_d_len = 1
        for stem in dicoStem:  # pour chaque stem
            df = dicoStem[stem]["df"]
            for doc in dicoStem[stem]:  # pour chaque document
                if doc != 'df':
                    try:
                        tf = log10(abs((dicoStem[stem][doc] * (k+1)) / (dicoStem[stem][doc] + k * (1 - b + b * df / avg_d_len))))
                    except:
                        tf = 0.0000001
                    dicoStem[stem][doc] = tf
        return dicoStem
    
    
    def genereIndexTF(self):
        """
        genere l'index ainsi aue l'index inversé methode main()
        """
        index = self.docs2dicoDoc() # preparation de l'index et calcul du TF
        indexDF = self.calculeDFdico(index) # ajouter les DF pour chque fichier
        reversIndex = self.dicoDoc2dicoStem(indexDF) # preparation de l'index inversé
        reversIndexDF = self.calculeDFdico(reversIndex) # calcul le total "df"
        reversIndexTF = self.calculenormalizedTFdico(reversIndexDF) # calcul le TF * IDF normalisé dans le fichier
        return index, reversIndexTF
    
if __name__ == "__main__":
    print(Indexeur_inverse().genereIndexTF()[1])