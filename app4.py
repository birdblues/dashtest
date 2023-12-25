
from dash import *
import dash_bootstrap_components as dbc
import dash_tvlwc as tvlwc
from data_generator import generate_random_ohlc, generate_random_series
from bitget_data import BitgetData

app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

data = BitgetData()

chart = tvlwc.Tvlwc(
    id='tv-chart-1',
    seriesData=[data.get_volume_json()],
    seriesTypes=['line'],
    width='100%',
    chartOptions= {
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