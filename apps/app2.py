import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table as dt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scipy.stats import poisson
from models import MarkovChainEstimator
#from mount_app_ import dash_app as app

from dash_server import dash_app as app, server
import random
import json

try:
    with open('data_store.json') as json_file:
        data = json.load(json_file)
    filename = data["filename"]
    filename = "pruebafinal.csv"
except:
    filename = None


if filename is None:    
    layout = html.Div([])
else:
    df_validation  = pd.read_csv(f"data/{filename}",index_col=0)
    df_validation.reset_index(drop= True, inplace = True)


    estimator = MarkovChainEstimator(df_validation)

    df = estimator.transition_matrix_df()
    df = df.round(2)
    df.reset_index(inplace=True)
    df.rename(columns = {'tipo':'event'})

    mc = estimator.markov_chain()
    fig_markov = estimator.plot_markov_chain(estimator.markov_chain)

    # padding for the page content
    CONTENT_STYLE = {
        "margin-left": "10rem",
        "margin-right": "10rem",
        "padding": "2rem 1rem",
    }

    layout = html.Div([
        html.Div([
            dbc.Button("Arrival distributions", color="primary", className="me-1",href='/apps/app1'),
            dbc.Button("Process distributions", color="primary", className="me-1",href='/apps/app3'),
                ]),


        html.Br(), 


            html.H2('Routing probabilities'),
            html.Br(), 
            html.Br(),   
            html.H3('Markov Chain Properties'),
            html.Br(), 
            dbc.Row(
                            [

                                dbc.Card(
                                            [

                                                dbc.CardBody(
                                                    [
                                                        html.H4("Markov Property", className="card-title"),
                                                        html.P(
                                                            "Q statistic is:  4535.63 p-value is:  1.0",
                                                            className="card-text",
                                                        ),                                            
                                                    ]
                                                ),
                                            ],
                                            style={"width": "25rem", "lenght": "10rem", "padding": "2px 16px"},
                                            color="light", outline=True,

                                        ),


                                 dbc.Card(
                                            [

                                                dbc.CardBody(
                                                    [
                                                        html.H4("First order Markov Chain", className="card-title"),
                                                        html.P(
                                                            "Q statistic is:  6878447.46 p-value is:  0.0",
                                                            className="card-text",
                                                        ),                                            
                                                    ]
                                                ),
                                            ],
                                            style={"width": "25rem", "lenght": "10rem", "padding": "2px 16px"},
                                            color="light", outline=True
                                        ),

                                 dbc.Card(
                                            [

                                                dbc.CardBody(
                                                    [
                                                        html.H4("Stationary probabilities", className="card-title"),
                                                        html.P(
                                                            "Q statistic is:  58447.26 p-value is:  1.0",
                                                            className="card-text",
                                                        ),                                            
                                                    ]
                                                ),
                                            ],
                                            style={"width": "25rem", "lenght": "10rem", "padding": "2px 16px"},
                                            color="light", outline=True
                                        )

                            ]
                        ),

        html.Br(), 
        html.Br(),   
        html.Br(), 
        html.H3('Transition matrix'),
        html.Br(),   
        dt.DataTable( id='table', columns=[{"name": i, "id": i} for i in df.columns],  data=df.to_dict('records') ),
        html.Br(),   
        html.H3('Transition graph',
                            style={'textAlign':'left'},
                            className="display-7"),

        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure = fig_markov)) , 
            ]),
       html.Br(),
       html.Br(),   



    ],style=CONTENT_STYLE)

    @app.callback(
        Output('app-2-display-value', 'children'),
        Input('app-2-dropdown', 'value'))
    def display_value(value):
        return 'You have selected "{}"'.format(value)








