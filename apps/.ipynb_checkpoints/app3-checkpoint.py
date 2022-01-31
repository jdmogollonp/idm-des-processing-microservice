import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scipy.stats import poisson
from models import DensityEstimator
#from mount_app_ import dash_app as app

from dash_server import dash_app as app, server
import random
from dash import dash_table as dt
from config import activity_pairs


import json
try:
    with open('data_store.json') as json_file:
        data = json.load(json_file)
    filename = data["filename"]
except:
    filename = None

if filename is None:    
    layout = html.Div([])
    
else:
    df_validation  = pd.read_csv(f"data/{filename}",index_col=0)
    
    df_validation.reset_index(drop= True, inplace = True)
    
    activities = activity_pairs.keys()

    CONTENT_STYLE = {
        "margin-left": "10rem",
        "margin-right": "10rem",
        "padding": "2rem 1rem",
    }

    layout = html.Div([

        html.Div([
            dbc.Button("Arrival distributions", color="primary", className="me-1",href='/apps/app1'),
            dbc.Button("Routing probabilities", color="primary", className="me-1",href='/apps/app2'),
                ]),
        html.Br(), 
        html.H4('Density distributions',
                            style={'textAlign':'left'},
                            className="display-7"),
                    html.Br(),         
         dcc.Dropdown(
                    id = 'app-3-dropdown',
                    options=[{'label': f'{i}', 'value': i} for i,j in activity_pairs.items() ],               
                    placeholder="Select an starting activity",
                    value = ""   
         ),

        html.Div(id='app-3-display-value'),

    ],style=CONTENT_STYLE)

    @app.callback(
        Output('app-3-display-value', 'children'),
        Input('app-3-dropdown', 'value'))
    def display_value(value):
        try:
            estimator  = DensityEstimator(df_validation)
            plot = estimator.plot(value)
        except:
            pass
        return [   
                      dbc.Row(
                            [
                                dbc.Col(dcc.Graph(id='bargraph',figure= plot)  ,) , 
                                dbc.Card(
                                            [
                                                dbc.CardBody(
                                                    [
                                                        html.H4("Parameters", className="card-title"),
                                                        html.P(

                                                            estimator.dist_string,                                                        
                                                            className="card-text",
                                                        ),
                                                        dt.DataTable( id='table', columns=[{"name": i, "id": i} for i in estimator.dist_params.columns if estimator.dist_params is not None], 
                                                                     data=estimator.dist_params.to_dict('records') if estimator.dist_params is not None else "" ),
                                                    ]
                                                ),
                                            ],
                                            style={"width": "18rem", "lenght": "8rem", "padding": "2px 14px"},
                                            color="light", outline=True
                                        )
                            ]
                        ),
               ]

