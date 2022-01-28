#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 22:14:39 2022

@author: mockingbird
"""

import nltk

class Config:
    
    def __init__(self):	       
    	nltk.download('punkt')
        
if __name__ == "__main__":
    conf = Config()
