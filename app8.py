import random
from datetime import datetime, timedelta

import dash_tvlwc
import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc

from dash_tvlwc.types import ColorType, SeriesType
from data_generator import generate_random_ohlc, generate_random_series


def switch_between(current, options):
    return random.choice([opt for opt in options if opt != current])

panel1 = [
    html.Div(
        dash_tvlwc.Tvlwc(
            id='tv-chart-1',
            seriesData=[generate_random_ohlc(100, n=50)],
            seriesTypes=[SeriesType.Candlestick],
            width='100%',
            chartOptions={
                'layout': {
                    'background': {'type': ColorType.Solid, 'color': '#1B2631'},
                    'textColor': 'white',
                },
                'grid': {
                    'vertLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
                    'horzLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
                },
                'localization': {
                    'locale': 'en-US',
                    'priceFormatter': "(function(price) { return '$' + price.toFixed(2); })"
                }
            }
        ), style={'background': 'grey'}
    ),
    html.Button('Change chart type', id='change-chart-type'),
    html.Button('Change background color', id='change-background-color'),
    html.Button('Generate new candlestick data', id='generate-new-candlestick-data'),
    html.Button('Info', id='info-btn'),
    html.Div(id='tv-chart-1-event-info'),
]


p2data = [generate_random_series(v0=15, n=50), generate_random_series(v0=15, n=50)]
p2markers = [
    [
        {'time': p2data[0][15]['time'], 'position': 'belowBar', 'color': '#EEEEEE', 'shape': 'arrowUp', 'text': 'Buy'},
        {'time': p2data[0][20]['time'], 'position': 'aboveBar', 'color': '#EEEEEE', 'shape': 'arrowDown', 'text': 'Sell'}
    ],
]
p2pricelines = [
    [
        {'price': 15, 'color': '#ff5040', 'lineStyle': 0, 'title': 'RANDOM PRICE LINE', 'axisLabelVisible': True}
    ],
]

panel2 = [
    dash_tvlwc.Tvlwc(
        id='tv-chart-2',
        seriesData=p2data,
        seriesTypes=['area', 'line'],
        seriesOptions=[{'priceLineWidth': 2}, {'priceLineWidth': 1}],
        seriesMarkers=p2markers,
        seriesPriceLines=p2pricelines,
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
            'localization': {'locale': 'en-US'}
        }
    ),
    html.Button('Change price line', id='change-price-line'),
    html.Button('Change markers', id='change-markers'),
    html.Button('Change line color', id='change-line-color'),
]

app = dash.Dash(__name__, external_stylesheets=['./assets/stylesheet.css'])
app.layout = html.Div([
    html.H1('Callback interactivity'),
    dcc.Interval(id='timer', interval=1000),
    html.Div(className='container', children=[
        html.Div(className='one', children=panel1),
        html.Div(className='two', children=panel2),
        html.Div(className='three', children=[
            html.Button('Add a new chart', id='add'),
            html.Div(id='tv-chart-3')
        ]),
    ]),
])


# callbacks to demo
@app.callback(
    [Output('tv-chart-1', 'seriesData')],
    [Input('generate-new-candlestick-data', 'n_clicks')],
    [State('tv-chart-1', 'seriesData')],
    prevent_initial_call=True
)
def change_props(n, series_data):
    # parse date time in tradingview
    last_close_date = series_data[0][-1]['time']
    last_close_dt = datetime(last_close_date['year'], last_close_date['month'], last_close_date['day'])
    new_datapoint = generate_random_ohlc(
        t0=(last_close_dt + timedelta(days=1)).strftime('%Y-%m-%d'),
        v0=series_data[0][-1]['close'], n=1
    )
    series_data[0].extend(new_datapoint)
    return [series_data]


@app.callback(
    [Output('tv-chart-1', 'chartOptions')],
    [Input('change-background-color', 'n_clicks')],
    [State('tv-chart-1', 'chartOptions')],
    prevent_initial_call=True
)
def change_props(n, current_chart_options):
    current_chart_options['layout']['background']['color'] = switch_between(
        current_chart_options['layout']['background']['color'], ['#1B2631', '#EEEEEE']
    )
    return [current_chart_options]


@app.callback(
    [Output('tv-chart-1', 'seriesTypes')],
    [Input('change-chart-type', 'n_clicks')],
    [State('tv-chart-1', 'seriesTypes')],
    prevent_initial_call=True
)
def change_props(n, series_types):
    series_types[0] = switch_between(series_types[0], ['bar', 'candlestick'])
    return [series_types]


@app.callback(
    [Output('tv-chart-2', 'seriesPriceLines')],
    [Input('change-price-line', 'n_clicks')],
    [State('tv-chart-2', 'seriesPriceLines')],
    prevent_initial_call=True
)
def change_props(n, series_price_lines):
    price_line_to_modify = series_price_lines[0][0]
    price_line_to_modify['price'] = 15 + random.uniform(-2, 2)
    series_price_lines[0] = [price_line_to_modify]
    return [series_price_lines]


@app.callback(
    [Output('tv-chart-2', 'seriesMarkers')],
    [Input('change-markers', 'n_clicks')],
    [State('tv-chart-2', 'seriesMarkers')],
    prevent_initial_call=True
)
def change_props(n, series_markers):
    markers_to_modify = series_markers[0]
    for markers in markers_to_modify:
        random_idx = switch_between(None, list(range(50)))
        markers['time'] = p2data[0][random_idx]['time']
    series_markers[0] = markers_to_modify
    return [series_markers]


@app.callback(
    [Output('tv-chart-2', 'seriesOptions')],
    [Input('change-line-color', 'n_clicks')],
    [State('tv-chart-2', 'seriesOptions')],
    prevent_initial_call=True
)
def change_props(n, series_options):
    series_options[1]['color'] = switch_between(series_options[1].get('color'), ['#FFCC00', '#5555FF'])
    return [series_options]


@app.callback(
    [Output('tv-chart-1-event-info', 'children')],
    [
        Input('tv-chart-1', 'crosshair'),
        Input('tv-chart-1', 'click'),
        Input('info-btn', 'n_clicks')
    ],
    [
        State('tv-chart-1', 'fullChartOptions'),
        # State('tv-chart-1', 'fullPriceScaleOptions'),
        # State('tv-chart-1', 'priceScaleWidth'),
        # State('tv-chart-1', 'fullSeriesOptions'),
        # State('tv-chart-1', 'timeRangeVisibleRange'),
        # State('tv-chart-1', 'timeRangeVisibleLogicalRange'),
        # State('tv-chart-1', 'timeScaleWidth'),
        # State('tv-chart-1', 'timeScaleHeight'),
        # State('tv-chart-1', 'fullTimeScaleOptions'),
    ],
    prevent_initial_call=True
)
def change_props(crosshair, click, n, options):
    crosshairhtml = []
    clickhtml = []
    optionshtml = []

    if crosshair is not None:
        for k, v in crosshair.items():
            crosshairhtml.append(html.Div([
                html.P(str(k)),
                html.P(str(v)),
            ]))
    if click is not None:
        for k, v in click.items():
            clickhtml.append(html.Div([
                html.P(str(k)),
                html.P(str(v)),
            ]))
    if options is not None:
        for k, v in options.items():
            optionshtml.append(html.Div([
                html.P(str(k)),
                html.P(str(v)),
            ]))
    # optionshtml.append(html.P(str(options)))
    return [
        html.Div(children=[
            html.Div(crosshairhtml),
            html.Div(clickhtml),
            html.Div(optionshtml)
        ])
    ]


@app.callback(
    [Output('tv-chart-3', 'children')],
    [Input('add', 'n_clicks')],
    prevent_initial_call=True
)
def add_chart(n):
    return [dash_tvlwc.Tvlwc(
        seriesData=[generate_random_series(v0=15, n=50), generate_random_series(v0=15, n=50)],
        seriesTypes=['area', 'line'],
        seriesOptions=[{'priceLineWidth': 2}, {'priceLineWidth': 1}],
        seriesMarkers=p2markers,
        seriesPriceLines=p2pricelines,
        # width='30%',
        chartOptions= {
            'layout': {
                'background': {'type': 'solid', 'color': '#1B2631'},
                'textColor': 'white',
            },
            'grid': {
                'vertLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
                'horzLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
            },
            'localization': {'locale': 'en-US'}
        }
    )]


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)