# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
import pandas as pd
from dash.dependencies import Input, Output
# Cache
from flask_caching import Cache
from drop_down import *


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Stock Dashboard'
application = app.server
cache = Cache(application, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT = 86400


@cache.memoize(timeout=TIMEOUT)
def query_data():
    # df = pd.read_csv('/Users/swain/Desktop/AWS/serverless-stock/data/cleaned-data(20200830).csv')
    df = pd.read_csv(
        'https://serverless-stocks.s3.amazonaws.com/stockinfos/cleaned_data/cleaned-data(20200830).csv')
    # df = pd.read_json(
    # 'https://serverless-stocks.s3.amazonaws.com/stockinfos/cleaned_data/2020-03-01(success)')
    df['trade_volume_shared'] = ['{:,}'.format(
        i) for i in df['trade_volume_shared']]

    df['transaction'] = ['{:,}'.format(
        i) for i in df['transaction']]

    df['trade_value'] = ['{:,}'.format(
        i) for i in df['trade_value']]

    df['opening_price'] = ['{:,}'.format(
        i) for i in df['opening_price']]

    df['closing_price'] = ['{:,}'.format(
        i) for i in df['closing_price']]

    df['change'] = ['{:,}'.format(
        i) for i in df['change']]

    df['price_earning_ratio'] = ['{:,}'.format(
        i) for i in df['price_earning_ratio']]

    return df


df = query_data()

print(df.columns)

app.layout = html.Div(children=[
    html.H1(children='Dashboard'),
    html.Div([
        html.P([
            html.Label('股票名稱'),
            html.Div([
                dcc.Dropdown(
                    id='stock-name-drop-down',
                    options=get_name_drop_down(df),
                    value='台泥',
                    searchable=True,
                    style={
                        'text-align': 'center',
                        'height': '38px'}
                ),
            ])
        ],
            style={'width': '200px',
                   'text-align': 'center',
                   'float': 'left'}
        ),
        html.P([
            html.Label('Y-axis(left)'),
            dcc.Dropdown(id='Y-axis(left)',
                         options=get_columns_drop_down(),
                         value='closing_price',
                         style={
                             'text-align': 'center',
                             'height': '38px'}
                         )],
               style={'width': '200px',
                      'text-align': 'center',
                      'float': 'left'}
               ),
        html.P([
            html.Label('Y-axis(right)'),
            dcc.Dropdown(id='Y-axis(right)',
                         options=get_columns_drop_down(),
                         value='trade_volume_shared',
                         style={
                             'text-align': 'center',
                             'height': '38px'}
                         )],
               style={'width': '200px',
                      'text-align': 'center',
                      'float': 'left'}
               ),
    ], style={'width': '50%', 'display': 'inline-block'}),

    dcc.Graph(
        id='stock-price',
    ),
    html.Div(children='''
        起始日期
    '''),
    dcc.Dropdown(
        id='stock-date-drop-down',
        options=get_date_drop_down(df),
        value='2018-01-02',
        style={
            'height': '35px',
            'width': '150px'
        },
        searchable=False
    ),
    dash_table.DataTable(
        id='stock-table',
        columns=[
            {'name': i, 'id': i} for i in table_columns()
        ],
        # data = df.to_dict('records'),
        # data = '',
        page_size=50
    )
])


@app.callback(
    Output('stock-price', 'figure'),
    [Input('stock-name-drop-down', 'value'),
     Input('Y-axis(left)', 'value'),
     Input('Y-axis(right)', 'value')]
)
def update_stock_price(stock_name, y_axis_left='closing_price', y_axis_right='trade_volume_shared'):
    dff = df[df['stock_name'] == stock_name]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=dff[dff['stock_name'] == stock_name]['date'],
                             y=dff[dff['stock_name'] == stock_name][y_axis_left], name=y_axis_left), secondary_y=False)

    fig.add_trace(go.Scatter(x=dff[dff['stock_name'] == stock_name]['date'],
                             y=dff[dff['stock_name'] == stock_name][y_axis_right], name=y_axis_right), secondary_y=True)

    fig.update_layout(
        title={
            'text': stock_name,
        })
    fig.update_layout(template='seaborn')
    return fig


@app.callback(
    Output('stock-table', 'data'),
    [Input('stock-name-drop-down', 'value'),
     Input('stock-date-drop-down', 'value')]
)
def update_stock_table(stock_name, stock_date):
    dff = df[df['stock_name'] == stock_name]
    dff = dff[dff['date'] >= stock_date]

    return dff.to_dict('records')


if __name__ == '__main__':
    application.run(debug=False, port=8080)
