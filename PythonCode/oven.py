import datetime
from turtle import delay
from attr import has
import serial
import os
import csv
import subprocess
from time import sleep
from thermocouples_reference import thermocouples
import dash
from dash import Dash, dash_table
from dash import dcc, html
import dash_daq as daq
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output, State
import pandas as pd

df = pd.read_csv('soldering.csv')

with open('soldering.csv', newline='') as f:
    reader = csv.reader(f)
    temp_list = list(reader)

temp_list.remove(temp_list[0])

typeK = thermocouples['K']
result = 0
old_result = 0
ser = serial.Serial('/dev/ttyACM0')

Pv = 0
Iv = 0
Dv = 0

timer = 0
soll_temp = 25
soll_time = 0
cycle = 0

isSoldering = False
hasStarted = False

def getData():
    global old_result
    pro = subprocess.Popen(os.getcwd()+"/getData", shell=True, stdout=subprocess.PIPE)
    try:
        result = str(pro.communicate()[0]).split(" ")
    except:
        pro.kill()
        result = pro.communicate

    try:
        result = float(result[1])
        if result > 20 :
            result = 888
    except:
        result = 999
    try:
        result = typeK.inverse_CmV(result, Tref=25)
        old_result = result 
    except:
        result = old_result
    return(result)



data = {
        'time': [],
        'oven_temp': [],
	    'soll_temp': [],
    }

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H1('Lötofen Controller'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        ),
	html.Div([
	html.H6('P :',style={'display':'inline-block','margin-right':20}),
	dcc.Input(id="Pv", type="number", placeholder="0", debounce=True)]),
	html.Div([
	html.H6('I : ',style={'display':'inline-block','margin-right':20}),
	dcc.Input(id="Iv", type="number", placeholder="0", debounce=True)]),
	html.Div([
	html.H6('D :',style={'display':'inline-block','margin-right':20}),
	dcc.Input(id="Dv", type="number", placeholder="0", debounce=True)]),
	daq.StopButton(id='ok_but',buttonText='OK',n_clicks=0),
    daq.StopButton(id='start_but',buttonText='Start',n_clicks=0),
    daq.StopButton(id='stop_but',buttonText='Stop',n_clicks=0),
	html.Div(id="output"),
    html.Div(id="output2"),
    html.Div(id="output3"),
    dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])])
)

@app.callback(
    Output("output", "children"),
    Input('ok_but', 'n_clicks'),
    State("Pv", "value"),
    State("Iv", "value"),
    State("Dv", "value"),
)
def update_output(n_clicks, input1, input2, input3):
    global Pv
    global Iv
    global Dv
    try:
        Pv = float(input1)
        Iv = float(input2)
        Dv = float(input3)
    except:
        Pv = Pv
    return u'P: {}, I: {}, D: {}'.format(input1, input2, input3)

@app.callback(
    Output("output3", "children"),
    Input('stop_but', 'n_clicks')
)
def stop_soldering(n_clicks):
    global isSoldering
    isSoldering = False
    ser.write(b'0')
    print("stop soldering")
    return ' '

@app.callback(
    Output("output2", "children"),
    Input('start_but', 'n_clicks'),
)
def start_soldering(n_clicks):
    global isSoldering
    global timer
    timer = 0
    isSoldering = True
    ser.write(b'0')
    print("start soldering")
    return ' '

@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))    
def textUpdate(n):
    oven_temp = getData()
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('Temperature: {0:.2f}'.format(oven_temp), style=style),
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    global hasStarted
    global isSoldering
    global cycle
    global soll_temp
    global timer
    global dat
    if(hasStarted == False):
        hasStarted = True
        isSoldering = False

    if(isSoldering == True and hasStarted == True):
        if (cycle > len(temp_list)-1):
            isSoldering = False
        elif (int(temp_list[cycle][0]) <= timer):
            cycle += 1
            soll_temp = temp_list[cycle][1]
        
        if (int(dat) < int(soll_temp) - 2):
            ser.write(b'1')
            len(temp_list)
        elif(int(dat) > int(soll_temp) + 2):
            ser.write(b'0')
            len(temp_list)
        timer += 2
    
    time = datetime.datetime.now()
    dat = getData()
    data['oven_temp'].append(dat)
    data['time'].append(time)
    data['soll_temp'].append(soll_temp)


    # Create the graph with subplots
    fig = go.Figure()
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.add_trace(go.Scatter(
        x= data['time'],
        y= data['oven_temp'],
        name= 'oven_temp',
        mode= 'lines+markers',
    ))
    fig.add_trace(go.Scatter(
        x= data['time'],
        y= data['soll_temp'],
        name= 'soll_temp',
        mode= 'lines+markers',
    ))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

