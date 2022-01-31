import uvicorn
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app




if __name__ == "__main__":
    uvicorn.run(app, port=8002)



#dev_tools_ui=False,dev_tools_props_check=False
#if __name__ == '__main__':
#    dash_app.run_server(debug=True,dev_tools_ui=False,dev_tools_props_check=False)


"""
from app import app,dash_app
from apps import app1, app2,app3

from fastapi.middleware.wsgi import WSGIMiddleware


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

"""