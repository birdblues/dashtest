
from dash import *
import dash_bootstrap_components as dbc
import dash_tvlwc as tvlwc
from transaction import TransactionData

app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG])
cyborg_colors = ["#2a9fd6", "#555", "#77b300", "#9933cc",
    "#ff8800", "#cc0000", "#222", "#000", "#fff"]

data = TransactionData()
sdata = data.get_profit_jason()
sType = ['line'] * len(sdata)
codes = data.get_code_list()
names = data.get_code_name()
sOption = []
for color, title in zip(cyborg_colors, names):
    sOption.append({
        'title': title,
        'color': color, 
        'axisLabelVisible': True,
    })

chart = tvlwc.Tvlwc(
    id='tv-chart-1',
    seriesData=sdata,
    seriesTypes=sType,
    seriesOptions=sOption,
    width='100%',
    chartOptions= {
        'timeScale': {
            'rightOffset': 5,
        },
        'layout': {
            'background': {'type': 'solid', 'color': '#1B2631'},
            'textColor': 'white',
        },
        'grid': {
            'vertLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
            'horzLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
        },
        'localization': {'locale': 'ko-KR'}
    }
) 

app.layout = dbc.Container(
    html.Div([
        html.H3(children='Title of Dash App', style={'textAlign':'left'}),
        chart,
    ])
)

if __name__ == "__main__":
    app.run_server(debug=True)