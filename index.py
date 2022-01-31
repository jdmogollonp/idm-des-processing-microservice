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


