# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 10:09:00 2021

@author: mockingbird
"""

import mongo_config

class Reset:
    def __init__(self):
        mongo_config.Mongo_Config().resetAll()
        
        
if __name__ == "__main__":
    Reset()