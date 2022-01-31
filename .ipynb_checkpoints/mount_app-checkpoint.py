from dash import dcc

from dash import html
from dash.dependencies import Input, Output


from fastapi.middleware.wsgi import WSGIMiddleware
from dash_server import dash_app, server

def mount_dash_app(app):

    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    @dash_app.callback(Output('page-content', 'children'),
                  Input('url', 'pathname'))
    def display_page(pathname):
        if pathname == '/apps/app1':
            return app1.layout
        elif pathname == '/apps/app2':
            return app2.layout
        elif pathname == '/apps/app3':
            return app3.layout
        else:
            return app1.layout

    app.mount("/", WSGIMiddleware(dash_app.server))
