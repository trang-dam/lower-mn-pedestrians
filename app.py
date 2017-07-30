import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly.graph_objs import *
import plotly.graph_objs as go
from flask import Flask
import pandas as pd
import datetime
import os
import json
import copy

app = dash.Dash()

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


mapbox_access_token = 'pk.eyJ1IjoiYWxpc2hvYmVpcmkiLCJhIjoiY2ozYnM3YTUxMDAxeDMzcGNjbmZyMmplZiJ9.ZjmQ0C2MNs1AzEBC_Syadg'


with open('./cam.txt', 'r') as f:
    cam = json.load(f)

df_d = pd.read_csv('input_date.csv')
df_d[['cam','count']] = df_d[['cam','count']].astype(int)
df_d['date'] = pd.to_datetime(df_d['date'], format='%Y-%m-%d')

df_t = pd.read_csv('input_hour.csv')

layout = dict(
    autosize=True,
    height=400,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    legend=dict(font=dict(size=10), orientation='h'),
)

app.layout = html.Div([
    html.Div([
        html.H1(
            'Pedestrians at Lower Manhattan by Hour/Day',
            # className='eight columns',
            # style={'text-align': 'center'},
        ),
        html.H2(
            '(Detected on NYC Department of Transportation Cameras)',
            # className='eight columns',
            # style={'text-align': 'center'},
        ),
    ], style={'text-align': 'center','margin': 'auto auto'}),    
    html.Div([
    dcc.Graph(
        id='map-graph',
        hoverData={'points': [{'customdata': 163}]},
        figure={
            'data': [
                Scattermapbox(
                    lat=[cam[i]['latlon'][1] for i in cam.keys()],
                    lon=[cam[i]['latlon'][0] for i in cam.keys()],
                    # names=cam.keys(),
                    hoverinfo="text",
                    text=[cam[i]['adr'] for i in cam.keys()],
                    customdata = cam.keys(), 
                    mode='markers',
                    marker=Marker(
                        opacity=0.5,
                        size=8,
                    ),
                ),
            ],    
                'layout': Layout(
                    autosize=True,
                    height=800,
                    margin=Margin(l=0, r=0, t=0, b=0),
                    showlegend=False,
                    mapbox=dict(
                        accesstoken=mapbox_access_token,
                        center=dict(
                            lat= 40.7272,
                            lon= -73.991251
                        ),
                        style='dark',
                        bearing=0,
                        zoom=12.2
                    ),    
                )
        }
    ),
    ], style={'width': '60%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='x-graph'),
        dcc.Graph(id='y-graph'),
    ], style={'display': 'inline-block', 'width': '40%','font-size': '12px'}),

  
])        

@app.callback(
    dash.dependencies.Output('x-graph', 'figure'),
    [dash.dependencies.Input('map-graph', 'hoverData')])
def update_xfigure(hoverData):
    # filtered_df = df_hour[['weekend','weekday',selected_date]]
    layout_y = copy.deepcopy(layout)
    cam = int(hoverData['points'][0]['customdata'])
    data = [
        dict(
            type='scatter',
            mode='lines+markers',
            name='WEEKDAY - cctv %s'%str(cam),
            x=df_t[(df_t['cam'] == cam) & (df_t['weekday'] == 1)]['hour'],
            y=df_t[(df_t['cam'] == cam) & (df_t['weekday'] == 1)]['count'],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color='#fac1b7'
            ),
            marker=dict(symbol='diamond-open')
        ),

        dict(
            type='scatter',
            mode='lines+markers',
            name='WEEKEND - cctv %s'%str(cam),
            x=df_t[(df_t['cam'] == cam) & (df_t['weekday'] == 0)]['hour'],
            y=df_t[(df_t['cam'] == cam) & (df_t['weekday'] == 0)]['count'],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color='#92d8d8'
            ),
            marker=dict(symbol='diamond-open')
        ),
    ]

    layout_y['title'] = 'Population over Hour'

    figure = dict(data=data, layout=layout_y)
    return figure


@app.callback(
    dash.dependencies.Output('y-graph', 'figure'),
    [dash.dependencies.Input('map-graph', 'hoverData')])
def update_yfigure(hoverData):
    # filtered_df = df_hour[['weekend','weekday',selected_date]]
    layout_y = copy.deepcopy(layout)
    cam = int(hoverData['points'][0]['customdata'])
    print(type(cam))
    data = [
        dict(
            type='scatter',
            mode='lines+markers',
            name='CCTV %s'%str(cam),
            x=df_d[df_d['cam'] == cam]['date'],
            y=df_d[df_d['cam'] == cam]['count'],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color='#F9ADA0'
            ),
            marker=dict(symbol='diamond-open')
        ),

        dict(
            type='scatter',
            mode='lines+markers',
            name='Lower Manhattan-Average',
            x=df_d[df_d['cam'] == cam]['date'],
            y=df_d.groupby('date').mean()['count'],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color='#849E68'
            ),
            marker=dict(symbol='diamond-open')
        ),
    ]

    layout_y['title'] = 'Population over Day'

    figure = dict(data=data, layout=layout_y)
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)

