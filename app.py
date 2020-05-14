from flask import Flask, render_template, request
import os
import sys
from os import listdir as ld
from os.path import join
from pathlib import Path as path
import re
import shutil
import json
import os
import pandas as pd
import numpy as np
import pickle
import collections
from importlib import reload
from os import listdir as ld
from datetime import datetime as dt
import json

import numpy as np

from time import time
import datetime
from datetime import timedelta
from dateutil import parser

import plotly_express as px
import plotly
import chart_studio.plotly as py
from chart_studio.grid_objs import Grid, Column
import plotly.figure_factory as ff
import plotly.graph_objects as go

#from IPython.display import display, Markdown, clear_output
import warnings
warnings.filterwarnings('ignore')
from main import plotla2


app = Flask(__name__)

togglebuttons = []
disagreetext = []

datetimeparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

lista='casos_anomalia_angulos.txt'
foco = 'Casos Anomalia de Angulos'
json_dir = "altas_rodada2"
current_dir = os.getcwd()
directory = current_dir + '/' + json_dir + '/'
list_filenames = []
list_dataini = []
list_datafim = []
list_instalacao = []


abas0 = {
    'potencias': 'tablinks',
    'angulos': 'tablinks',
    'tensoes': 'tablinks',
    'correntes': 'tablinks'
}
info0=['correntes','potencias','tensoes','angulos']
@app.route('/t3')
def teste():
    return render_template('index.html')


def build_page(page):
    with open(page,'r') as f:
        content = '{% extends index.html %} \n {% block content %} \n'+ f.read().splitlines(True)[3:] + '{% endblock %}'
    with open(page,'w') as f:
        f.writelines(content)
    

@app.route('/json', methods = ['POST'])
def postJsonHandler():
    print (request.is_json)
    jason= request.get_json()
    datetimeparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    togglebuttons = []
    disagreetext = []
    current_dir = os.getcwd()
    list_filenames = []
    list_dataini = []
    list_datafim = []
    list_instalacao = []
    d1 = dict(jason)
    instalacao=d1['info']['ponto_medicao']
    filename = instalacao + '.json'
    RTC=d1['info']['RTC']
    fas1 = pd.DataFrame(columns = d1['fasorial_columns'], data=d1['fasorial'].values(), index=d1['fasorial'].keys())
    dataif = fas1.index[0].split(' ')[0]
    dataff = fas1.index[-1].split(' ')[0]
    dmm1= d1['mm']
    databd = pd.DataFrame(index=dmm1.keys(), data=dmm1.values(), columns = ['memoria_de_massa'])
    databd.iloc[:,0]= databd.iloc[:,0].apply(float)
    datai = databd.index[0].split(' ')[0]
    dataf = databd.index[-1].split(' ')[0]    
    list_filenames.append(filename)
    list_dataini.append(datai)
    list_datafim.append(dataf)
    list_instalacao.append(instalacao)
    index=0 #hc
    togglebuttons, disagreetext = plotla2(fas1, instalacao, RTC, datai, dataf,'correntes', togglebuttons, disagreetext, index, foco)
    togglebuttons, disagreetext = plotla2(fas1, instalacao, RTC, datai, dataf,'potencias', togglebuttons, disagreetext, index, foco)
    togglebuttons, disagreetext = plotla2(fas1, instalacao, RTC, datai, dataf,'tensoes', togglebuttons, disagreetext, index, foco)
    togglebuttons, disagreetext = plotla2(fas1, instalacao, RTC, datai, dataf,'angulos', togglebuttons, disagreetext, index, foco)
    return render_template('index.html',insta=instalacao, info=info0, abas=abas0)

@app.route('/<instalacao>')
def template_index(instalacao):
    if '_' not in instalacao:
        print('-----------------TEMPLATIOON----------------',instalacao)
        return render_template('index.html',insta=instalacao, info=info0, abas=abas0)
    else:
        print('-----------------NOOITALPMET----------------',instalacao)
        insta= instalacao.split('_')[0]
        cols_selection=instalacao.split('_')[1].split('.html')[0]
        for k in abas0.keys():
            if k==cols_selection:
                abas0[k]='tablinks  active'
            else:
                abas0[k]='tablinks'
        return render_template(instalacao ,insta=insta,  info=info0, abas=abas0)
"""
@app.route('/<instalacao>/<informacao>')
def template_index(instalacao, informacao):
    print('-----------------TEMPLATIOON----------------',ios.path.join('cache',instalacao))nstalacao)
    return redirect(url_for((os.path.join('cache',instalacao, informacao+'.html'))))
"""

if __name__ == '__main__':
    app.run('0.0.0.0')
