#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 17:22:50 2022

@author: mockingbird
"""

import queryRanking
from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = 'projet_BDD[moteur_de_recherche]'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search',methods=['POST'])
def showSummary(): 
    try:
        search = request.form['search']
        if search != "":
            results, time = queryRanking.QueryRanking().start(search)
            # print(results)
            return render_template(
                'result.html',
                search = search.lower(), 
                total = len(results), 
                time = time, 
                results = results
                ), 200
    except:
        return render_template('index.html'), 403

if __name__ == '__main__':
    app.run()