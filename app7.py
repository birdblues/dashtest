import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_tvlwc
import dash_bootstrap_components as dbc
from pprint import pprint
from bitget_data import BitgetData

symbol = 'BTC/USDT:USDT'
data = BitgetData(symbol)
series = data.get_ohlc_json('5T', 300)
volume = data.get_volume_json('5T', 300)
forcast = data.get_yhat_json('15T', '5T', 300)
# yhat = [{'time': i['time'], 'value': i['value']} for i in forcast]
yhat = forcast[0]
yhat_lower = forcast[1]
yhat_upper = forcast[2] 

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

button_group = dbc.ButtonGroup(
    [
        dbc.Button(" 1m", outline=True, color="dark", size="sm", id='btn-1m', active=False, value='1T'),
        dbc.Button(" 5m", outline=True, color="dark", size="sm", id='btn-5m', active=True, value='5T'),
        dbc.Button("15m", outline=True, color="dark", size="sm", id='btn-15m', active=False, value='15T'),
        dbc.Button("30m", outline=True, color="dark", size="sm", id='btn-30m', active=False, value='30T'),
        dbc.Button(" 1H", outline=True, color="dark", size="sm", id='btn-1h', active=False, value='1H'),
        dbc.Button(" 4H", outline=True, color="dark", size="sm", id='btn-4h', active=False, value='4H'),
        dbc.Button(" 1D", outline=True, color="dark", size="sm", id='btn-1D', active=False, value='1D'),
    ], id='active-button'
)

button_group2 = dbc.ButtonGroup(
    [
        dbc.Button(" 5m", outline=True, color="warning", size="sm", id='fbtn-5m', active=False, value='5T', disabled=True),
        dbc.Button("15m", outline=True, color="warning", size="sm", id='fbtn-15m', active=True, value='15T', disabled=False),
        dbc.Button("30m", outline=True, color="warning", size="sm", id='fbtn-30m', active=False, value='30T', disabled=False),
        dbc.Button(" 1H", outline=True, color="warning", size="sm", id='fbtn-1h', active=False, value='1H', disabled=False),
        dbc.Button(" 4H", outline=True, color="warning", size="sm", id='fbtn-4h', active=False, value='4H', disabled=False),
        dbc.Button(" 1D", outline=True, color="warning", size="sm", id='fbtn-1D', active=False, value='1D', disabled=False),
    ], id='forcast-button'
)

button_group3 = dbc.ButtonGroup(
    [
        dbc.Button("LIVE", outline=True, color="danger", size="sm", id='btn-live', active=True),
    ], id='test-button'
)

import datetime
date_string = "2023-12-24"
date_object = datetime.datetime.strptime(date_string, "%Y-%m-%d")
epoch_time = int(date_object.timestamp())

markers = [
    {'time': series[-1]['time'], 'position': 'aboveBar', 'color': '#f68410', 'shape': 'circle', 'text': 'Signal'},
]

chart = html.Div(children=[
    dash_tvlwc.Tvlwc(
        id='candlestick-chart',
        seriesMarkers=[
            [ 
                {
                    'time': series[-1]['time'],  # The date/time where the line should be drawn
                    'color': 'red',  # The color of the line
                    'id': 'marker1',  # The id of the marker
                    'lineWidth': 2,  # The width of the line
                    'lineStyle': 0,  # The style of the line (0 = Solid, 1 = Dotted, 2 = Dashed, 3 = Large Dashed)
                }
            ]
        ],
        seriesData=[series, volume, yhat, yhat_lower, yhat_upper],
        seriesTypes=['candlestick', 'histogram', 'line', 'line', 'line'],
        seriesOptions=[
            {
                'priceLineWidth': 2,
                'title': 'BTC/USDT',
                'axisLabelVisible': True,
                'scaleMargins': {'top': 0, 'bottom': 0.2},
            },
            {
                'color': '#26a69a',
                'priceFormat': {'type': 'volume'},
                'priceScaleId': '',
                'scaleMargins': {'top': 0.8, 'bottom': 0},
                'priceLineVisible': True,
            },
            {   
                # 'lineWidth': 1,
                # 'color': 'yellow',
                # 'lastPriceAnimation': True, # Whether to animate the last price change
                'priceLineVisible': False,
                'color': '#f68410',
            },
            {
                'lineWidth': 1,
                'lineStyle': 0,
                'priceLineVisible': False,
                'color': '#f68410',
            },
            {
                'lineWidth': 1,
                'lineStyle': 0,
                'priceLineVisible': False,
                'color': '#f68410',
            }
        ],
        width='100%',
        height='600px',
        chartOptions= {
            'crosshair': {
                'mode': 0,
            },
            # 'rightPriceScale': {
            #     'autoScale': False,
            #     'scaleMargins': {'top': 0, 'bottom': 0},
            # },
            # 'overlayPriceScales': {
            #     'autoScale': False,
            # },
            'handleScroll': {
                # "mouseWheel": False,
                # "pressedMouseMove": True,
                # "horzTouchDrag": False,
                # "vertTouchDrag": False,
            },
            "handleScale": {
                "axisPressedMouseMove": True,
                "mouseWheel": True,
                # "pinch": False,
            },
            'timeScale': {
                'shiftVisibleRangeOnNewBar': False,
                'allowShiftVisibleRangeOnWhitespaceReplacement': False,
                'rightOffset': 20,
                # 'fixLeftEdge': True,  
                # 'fixRightEdge': True,
                'lockVisibleTimeRangeOnResize': True,
                'borderVisible': True,
                'rightBarStaysOnScroll': False,
                'timeVisible': True,
                'secondsVisible': True,
            },
            'layout': {
                'background': {'type': 'solid', 'color': '#1B2631'},
                'textColor': 'white',
            },
            'grid': {
                'vertLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
                'horzLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
            },
            'localization': {
                'locale': 'ko-KR',
                'priceFormatter': "(function(price) { return price.toFixed(2); })"
            }
        }
    ),
])

app.layout = dbc.Container(
    html.Div([
        html.H3(children=symbol, style={'textAlign':'left'}),
        dbc.Stack([ button_group, button_group2, button_group3 ], direction="horizontal", gap=2),
        chart,
        dcc.Interval(
        id='timer',
        interval=1000, # 밀리초 단위로 시간 간격 설정 (여기서는 1초)
        n_intervals=0
    )
    ])
)

@app.callback(
    [Output('candlestick-chart', 'seriesData')],
    [Input('timer', 'n_intervals')],
    [State('candlestick-chart', 'seriesData'),
     State('candlestick-chart', 'chartOptions'),
     State('active-button', 'children'),
     State('forcast-button', 'children'),
    ],
    prevent_initial_call=False
)
def update_data(n, series_data, options, children1, children2):
    pprint(options) 
    active = [i for i in children1 if i['props']['active'] == True]
    if len(active) == 0:
        timeframe = '5T'
    else:
        timeframe = active[0]['props']['value']
    series_data[0] = data.get_ohlc_json(timeframe, 1000)
    series_data[1] = data.get_volume_json(timeframe, 1000)

    active = [i for i in children2 if i['props']['active'] == True]
    if len(active) == 0:
        outtp = '15T'
    else:
        outtp = active[0]['props']['value']
    print(timeframe, outtp)

    forcast = data.get_yhat_json(outtp, timeframe, 1000)
    series_data[2] = forcast[0]
    series_data[3] = forcast[1]
    series_data[4] = forcast[2]
    return [series_data]
    
@app.callback(
    [Output('active-button', 'children'),
     Output('forcast-button', 'children'),
     Output('timer', 'disabled', allow_duplicate=True), 
     Output('btn-live', 'active', allow_duplicate=True), 
    ],
    [Input('btn-1m', 'n_clicks_timestamp'),
     Input('btn-5m', 'n_clicks_timestamp'),
     Input('btn-15m', 'n_clicks_timestamp'),
     Input('btn-30m', 'n_clicks_timestamp'),
     Input('btn-1h', 'n_clicks_timestamp'),
     Input('btn-4h', 'n_clicks_timestamp'),
     Input('btn-1D', 'n_clicks_timestamp'),
     Input('fbtn-5m', 'n_clicks_timestamp'),
     Input('fbtn-15m', 'n_clicks_timestamp'),
     Input('fbtn-30m', 'n_clicks_timestamp'),
     Input('fbtn-1h', 'n_clicks_timestamp'),
     Input('fbtn-4h', 'n_clicks_timestamp'),
     Input('fbtn-1D', 'n_clicks_timestamp'),
    ],
    [State('active-button', 'children'),
     State('forcast-button', 'children'),
    ],
    prevent_initial_call=True
)
def update_active_button(t1, t2, t3, t4, t5, t6, t7, 
                        f1, f2, f3, f4, f5, f6,
                        children1, children2):
    timestamps = [t or 0 for t in [t1, t2, t3, t4, t5, t6, t7, f1, f2, f3, f4, f5, f6,]]
    if sum(timestamps) > 0:
        found = False
        for i in children1:
            if 'n_clicks_timestamp' in i['props']:
                if i['props']['n_clicks_timestamp'] == max(timestamps):
                    found = True
        if found:
            for i in children1:
                i['props']['active'] = False
                if 'n_clicks_timestamp' in i['props']:
                    if i['props']['n_clicks_timestamp'] == max(timestamps):
                        i['props']['active'] = True
                        index = children1.index(i)
                        for j in children2:
                            if children2.index(j) < index:
                                j['props']['disabled'] = True
                            else:
                                j['props']['disabled'] = False
                        need = False
                        for j in children2:
                            if j['props']['active'] == True:
                                if j['props']['disabled'] == True:
                                    need = True
                        if need:
                            for j in children2:
                                j['props']['active'] = False
                                if children2.index(j) == index:
                                    j['props']['active'] = True
        else:
            for i in children2:
                i['props']['active'] = False
                if 'n_clicks_timestamp' in i['props']:
                    if i['props']['n_clicks_timestamp'] == max(timestamps):
                        i['props']['active'] = True
                    
    return [children1, children2, False, True]


@app.callback(
    [Output('timer', 'disabled', allow_duplicate=True),
     Output('btn-live', 'active'),],
    [Input('btn-live', 'n_clicks')],
    [State('timer', 'disabled')],
    prevent_initial_call=True
)
def change_props(n, diasbled):
    if diasbled:
        return [False, True]
    else:
        return [True, False]

@app.callback(
    [Output('candlestick-chart', 'seriesPriceLines')],
    [Input('timer', 'n_intervals')],
    [State('candlestick-chart', 'seriesData')],
    prevent_initial_call=True
)
def change_props(n, seriesData):
    pricelines = [
        [
            {'price': 43600, 'color': '#ff5040', 'lineStyle': 0, 'title': 'RANDOM PRICE LINE', 'axisLabelVisible': True}
        ],
    ]

    return [pricelines]

if __name__ == '__main__':
    app.run_server(debug=True)