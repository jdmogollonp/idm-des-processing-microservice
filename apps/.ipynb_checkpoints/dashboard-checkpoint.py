import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app


# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H5("Process statistics", className="display-6"),
        html.Hr(),        
        dbc.Nav(
            [
                dbc.NavLink("Arrival", href="apps/app1", active="exact"),
                dbc.NavLink("Routing probabilities", href="apps/app2", active="exact"),
                dbc.NavLink("Process distributions", href="apps/app3", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],    style=SIDEBAR_STYLE,
)

layout = html.Div([
    dcc.Location(id="url"),
    sidebar,

])



    

