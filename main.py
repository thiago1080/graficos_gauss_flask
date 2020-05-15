import plotly_express as px
import chart_studio.plotly as py
from chart_studio.grid_objs import Grid, Column
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import os
import pickle

from IPython.display import display, Markdown, clear_output
import ipywidgets as widgets

colunas = {
    'potencias': ['IA','IB','IC', 'PA', 'PB', 'PC'],
    'angulos': ['VA','VB','VC','AVAB','AVBC','AVAC'],
    'tensoes': ['VA','VB','VC','AVAB','AVBC','AVAC'],
    'correntes': ['IA','IB','IC', 'VA', 'VB', 'VC']
}

translate = {
    'potencias':'POTÊNCIAS',
    'angulos': 'ÂNGULOS',
    'tensoes': 'TENSÕES',
    'correntes': 'CORRENTES'
}

def max_min_table(colunas, cols_selection ,databd):
    s=''
    s+='<table> <tr> <th> Coluna </th> <th> Mínimo</th> <th> Máximo</th> </tr>'
    for i in colunas[cols_selection]:
        s+=('<tr>')
        s+=(f'<td><b>{i}</b></td>')
        s+=(f'<td>{np.min(databd[i]).round(decimals=0)}</td>')
        s+=(f'<td>{np.max(databd[i]).round(decimals=0)}</td>')
        s+=('</tr>')
    s+='</table>'
    return s

def build_page(page,colunas, cols_selection,databd):
    with open(page,'r') as f:
        content = ['{% extends "index.html" %} \n' ,'{% block content %} \n']
        content.append('<div id=maindiv>')
        content.append(max_min_table(colunas,cols_selection,databd))
        content.extend(f.read().splitlines(True)[4:-2])
        content.append('{% endblock %}')
    with open(page,'w') as f:
        f.writelines(content)



def query_oracle(command):
    username = 'gauss'
    dsn = '10.3.79.132/HMLHVP'
    dsn2 = '10.3.79.132/SID:HMLHVP'
    dsn3 = '10.3.79.132'
    port = 1521
    password = 'scluster'
    #command = open('consulta.sql').read().split(';')[0]
    connection = None
    try:
        connection = cx_Oracle.connect(
            username,
            password,
            dsn,
            encoding='UTF-8')
        cursor = connection.cursor()
        infos = cursor.execute(command)
        blob = infos.fetchone()[7] 
        bytess = blob.read()
    except cx_Oracle.Error as error:
        print(error)
    return bytess    
# finally:
#      if connection:
#         connection.close()

def plotla2(databd, instalacao, RTC, datai, dataf, cols_selection, togglebuttons, disagreetext, index, foco):

    info_text='<br>'
    html = "templates/" #hc
    proj="P&D Light"
    cols = colunas[cols_selection]
    togglebuttons.append(widgets.ToggleButtons(name='a', options=['Concordo ', 'Discordo '],description='',disabled=False,button_style='primary',
                              tooltips=['Caso deveria ser levantado pelo GAUSS', 'Caso não deveria ser levantado pelo GAUSS'],
                              icons=['thumbs-up','thumbs-down']))
    disagreetext.append(widgets.Text(value='', placeholder='Motivo discordancia', description='', disabled=False))


    descr = "Instalacao "+instalacao
    fig = make_subplots(rows=3, cols=1, specs=[[{"secondary_y": True}],[{"secondary_y": True}],[{"secondary_y": True}]])



    if cols_selection == 'potencias':
        databd = calcula_potencia_corrente(RTC, databd, cols_selection)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['IA'], name='iA', line=dict(width=1)),row=1,col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['PA'], name='pA'),row=1,col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['IB'], name='iB', line=dict(width=1)),row=2,col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['PB'], name='pB'),row=2,col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['IC'], name='iC', line=dict(width=1)),row=3,col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['PC'], name='pC'),row=3,col=1, secondary_y=False)
        fig.update_yaxes(title_text="Potencia", secondary_y=False)
        fig.update_yaxes(title_text="Corrente", secondary_y=True)

    if cols_selection == 'angulos': 
        fig.add_trace(go.Barpolar(name = "avA", r = [max(databd['VA'])]*len(databd['AVA']), theta=databd['AVA'], width=[1]*len(databd['AVA']),marker_color=['blue']*len(databd['AVA']),marker_line_color='blue',marker_line_width=2, opacity=0.8))
        fig.add_trace(go.Barpolar(name = "avB",r = [max(databd['VB'])]*len(databd['AVB']), theta=databd['AVB'], width=[1]*len(databd['AVB']),marker_color=['green']*len(databd['AVB']), marker_line_color='green', marker_line_width=2, opacity=0.8))
        fig.add_trace(go.Barpolar(name = "avC",r = [max(databd['VC'])]*len(databd['AVC']), theta=databd['AVC'], width=[1]*len(databd['AVC']),marker_color=['red']*len(databd['AVC']), marker_line_color='red', marker_line_width=2, opacity=0.8))
        fig.update_layout(
            polar = dict(
                radialaxis_angle = 90,
                radialaxis = dict(range=[0, max(max(databd['VA']),max(databd['VB']),max(databd['VC']))], showticklabels=True),
                angularaxis = dict(direction = "counterclockwise", dtick = 10))
            )
    if cols_selection == 'correntes':   
        fig.add_trace(go.Scatter(x=databd.index, y=databd['IA'], name='iA'),row=1,col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['VA'], name='vA'),row=1,col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['IB'], name='iB'),row=2,col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['VB'], name='vB'),row=2,col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['IC'], name='iC'),row=3,col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['VC'], name='vC'),row=3,col=1, secondary_y=False)
        fig.update_yaxes(range=[-5, 150], secondary_y=False)
        fig.update_yaxes(title_text="Tensão", secondary_y=False)
        fig.update_yaxes(title_text="Corrente", secondary_y=True)

    if cols_selection == 'tensoes':
        fig = make_subplots(rows=3, cols=1, specs=[[{"secondary_y": True}],[{"secondary_y": True}],[{"secondary_y": True}]])  
        fig.add_trace(go.Scatter(x=databd.index, y=databd['VA'], name='vA'),  row=1,col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['VAB'], name='vAB'),row=1,col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['VB'], name='vB'),  row=2,col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['VBC'], name='vBC'),row=2,col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['VC'], name='vC'),  row=3,col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=databd.index, y=databd['VAC'], name='vAC'),row=3,col=1, secondary_y=False)
        fig.update_yaxes(title_text="Fase", secondary_y=True)
        fig.update_yaxes(title_text="Entre Fases", secondary_y=False)
    fig.update_layout(
    title=go.layout.Title(
        text=f'<b>{instalacao} - {translate[cols_selection]}</b><br><b>{datai} a {dataf}</b><br><b>Sequência: {str(databd["FREQ"].unique()[0])}</b>',
        xref="paper",
        font=dict(family='Courier New, monospace', size=14),
        x=0)
    )

    html_file = os.path.join(html,instalacao+'_'+cols_selection+".html")
    fig.update_layout(dict1={'font':{'size':10}})
    fig.update_layout(legend_orientation="h")
    fig.write_html(html_file, auto_open=False)
    build_page(html_file,colunas, cols_selection,databd)
    

    return togglebuttons, disagreetext

def calcula_potencia_corrente (RTC, databd, cols_selection):
    cols = colunas[cols_selection]
    sRTC = RTC.split('/')
    num=int(sRTC[0])
    den=int(sRTC[1])
    rel=num/den
    for col in cols:
        databd[col]=databd[col].apply(lambda x: x*rel)
    return databd






def plot_tensao_corrente(databd, instalacao, RTC, datai, dataf, cols_selection, togglebuttons, disagreetext, index, foco):
    #ajuste da correlação para evitar NAN quando todos os valores são zerados
    correlation_ipA = 0
    correlation_ipB = 0
    correlation_ipC = 0

    if (not np.isnan(databd['IA'].corr(databd['PA']))):
        correlation_ipA = databd['IA'].corr(databd['PA'])
    
    if (not np.isnan(databd['IB'].corr(databd['PB']))):
        correlation_ipB = databd['IB'].corr(databd['PB'])
    
    if (not np.isnan(databd['IC'].corr(databd['PC']))):
        correlation_ipC = databd['IC'].corr(databd['PC'])
    
    fig1 = make_subplots(rows=3, cols=1, specs=[[{"secondary_y": True}],[{"secondary_y": True}],[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(x=databd.index, y=databd['IA'], name='IA'),row=1,col=1, secondary_y=True)
    fig1.add_trace(go.Scatter(x=databd.index, y=databd['VA'], name='VA'),row=1,col=1, secondary_y=False)
    fig1.add_trace(go.Scatter(x=databd.index, y=databd['IB'], name='IB'),row=2,col=1, secondary_y=True)
    fig1.add_trace(go.Scatter(x=databd.index, y=databd['VB'], name='VB'),row=2,col=1, secondary_y=False)
    fig1.add_trace(go.Scatter(x=databd.index, y=databd['IC'], name='IC'),row=3,col=1, secondary_y=True)
    fig1.add_trace(go.Scatter(x=databd.index, y=databd['VC'], name='VC'),row=3,col=1, secondary_y=False)
    fig1.update_yaxes(title_text="Corrente", secondary_y=True)
    fig1.update_yaxes(title_text="Tensão", secondary_y=False)

    fig1.update_layout(
        legend_orientation="h",
        title=go.layout.Title(
            text='TEXT_PLACEHOLDER')
    )
    html = "/var/www/html/FlaskApp/FlaskApp/cache/"
    html_file = join(html,instalacao,cols_selection+".html")
    print('-------------------------------------')
    print(html_file)
    fig1.write_html(html_file, auto_open=True)
    #img1_file = images_dir+row['Nome']+"img1.png"
    #fig1.write_image(img1_file)

