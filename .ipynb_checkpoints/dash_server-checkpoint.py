import dash
from dash import dcc
import dash_bootstrap_components as dbc
dash_app = dash.Dash(__name__, suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.BOOTSTRAP])
server = dash_app.server
