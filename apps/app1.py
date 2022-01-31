import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scipy.stats import poisson
from models import ArrivalEstimator
from dash_server import dash_app as app, server
import random
import json

try:
    with open('data_store.json') as json_file:
        data = json.load(json_file)
    filename = data["filename"]
except:
    filename = None



filename = data["filename"]
filename = "pruebafinal.csv"

if filename is None:    
    layout = html.Div([])
else:
    df_validation  = pd.read_csv(f"data/{filename}",index_col=0)
    df_validation.reset_index(drop= True, inplace = True)
    df_validation = df_validation[df_validation.stage == "arrival"]
    estimator = ArrivalEstimator(df_validation)
    estimator.fit()
    fig_arrival_estimator  = estimator.nh_poisson()


    # padding for the page content
    CONTENT_STYLE = {
        "margin-left": "10rem",
        "margin-right": "10rem",
        "padding": "2rem 1rem",
    }


    layout = html.Div([


        html.Div(
        [
            dbc.Button("Routing probabilities", color="primary", className="me-1",href='/apps/app2'),
            dbc.Button("Process distributions", color="primary", className="me-1",href='/apps/app3'),
                ]),

          html.Br(), 


        html.H4('Arrivals',
                            style={'textAlign':'center'},
                            className="display-7"),
                    html.Br(),            


                    html.H5('Estimated hourly patients arrival rate',
                            style={'textAlign':'left'},
                            className="display-7"),

                    dbc.Row(
                            [
                                dbc.Col(dcc.Graph(id='bargraph',figure= fig_arrival_estimator)  ,) , 

                            ]
                        ),
                    html.Br(),

        dcc.Dropdown(
                    id = 'app-1-dropdown',
                    options=[{'label': f'{i+1} h', 'value': round(j)} for i,j in estimator.nhpp_hour_lambda_dict.items() ],               
                    placeholder="Select an hour of the day",
                    value = ""
                        ),
        html.Div(id='app-1-display-value')
    ],style=CONTENT_STYLE)

    @app.callback(
        Output('app-1-display-value', 'children'),
        Input('app-1-dropdown', 'value'))
    def display_value(value):
        value = round(random.choice(list(estimator.nhpp_hour_lambda_dict.values())))
        return [
            html.Br(),
            html.H5('Arrival distribution',
                            style={'textAlign':'left'},
                            className="display-7"),

            dbc.Row(
                            [
                                dbc.Col(dcc.Graph(id='graph-poisson',figure= estimator.plot_poisson(value))   ,) , 


                            ]
                        ),
            html.Br(),

            html.H5('Inter-arrivals distribution',
                            style={'textAlign':'left'},
                            className="display-7"),

            dbc.Row(
                            [
                                dbc.Col(dcc.Graph(id='graph-poisson',figure= estimator.plot_exponential(value))   ,) , 


                            ]
                        ),

               ]

