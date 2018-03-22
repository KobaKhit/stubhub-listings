# -*- coding: utf-8 -*-
from dash_responsive import Dash_responsive 
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import plotly.graph_objs as go

import pandas as pd
import numpy as np

from stubhub_scraper import St

import urllib
import re
from textwrap import dedent as d
import json
import sys




def spacer(text):
    return re.sub(r'([A-Z])',r" \1",text).strip()

styles = {
    'datatable':{'font-size':'12px'}
}


# Enter user's API key, secret, and Stubhub login
app_token = '7131e534-bbec-374f-b1e4-1bdf6909a8ee'
consumer_key = 'jC475_MWRt6VV0aRz6nhA4Kpfloa'
consumer_secret = 'U7bW44Spj64CDYwUQSofJaMh1zka'
stubhub_username = ''
stubhub_password = ''

df = pd.read_csv('flyers listings.csv')
df = df.loc[(df['Event']=='Washington Capitals 3/18/2018'),:]
df = df.rename(spacer,axis='columns')

DESC = '''This app enables you to download all stubhub listings for a given event id. 
           I developed it using [Dash](https://plot.ly/products/dash/) and my [stubhub API](https://github.com/KobaKhit/stubhubAPI) 
          python wrapper.
'''

app = Dash_responsive()
app.title = 'Stuhub Listings'
server = app.server

app.layout = html.Div(children=[

    html.Div([
        html.Div([
            html.H1(children='Stubhub Listings'),

            html.Div(children='''
                Enter event id and press submit.
            '''),
            html.Div(['stubhub.com/<event-name>/event/',
                      html.Strong('103511793')], style = {'color':'purple'}),
            html.Div([
            dcc.Input(id='input-1-state', type='text', value=''),
            html.Button(id='submit-button', n_clicks=0, children='Submit'),
            html.Div(id='output-state'),
            html.Div(id='cache', style={'display': 'none'})])

            ], 
        className='six columns'),

        html.Div([
            html.Div(children=[html.Br(),dcc.Markdown(DESC), 
                               'Created in haste ',
                               # html.I(className="fa fa-heart"), 
                               ' by ',
                               html.A('kobakhit',href='http://www.kobakhit.com/',target='_blank')]
            ,className = 'container')], 
        className='six columns', style = {'text-align':'right'})
    ], className = 'row'),

    # dcc.Tabs(
    #     tabs=[
    #         {'label': 'Histograms','value': 1},
    #         {'label': 'Heatmap','value': 2} 
    #     ],
    #     value=1,
    #     id='tabs'
    # ),
    # html.Div(id='tab-output'),

    html.Div([
        html.Div([
                dcc.Graph(id='g1', figure={'data': []})
            ], className="six columns"),

        html.Div([
                dcc.Graph(id='g2', figure={'data': []})
            ], className="six columns")
    ],className = 'row'),

    html.Div([
        html.Div([
                dcc.Markdown(d("""
                    **Selection Data**
                    Choose the lasso or rectangle tool in the graph's menu
                    bar and then select bars in the graph.
                """))
            ], className="twelve columns")
    ],className = 'row'),

     html.A(
        'Download All Listings',
        id='download-link',
        download="all_stubhub_listings.csv",
        href="",
        target="_blank"
    ),

    html.Div(id = 'datatable', children = [
        dt.DataTable(
            rows=[{}],

            # optional - sets the order of columns
            # columns=sorted(df.columns),

            # row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id='datatable-df'
        )
    ],style=styles['datatable']),

    html.Div([
                dcc.Graph(id='heatmap', figure={'data': []}, style={'height':'800px','font-size': '10px'})
            ])
])


# sort mixed list
def sort_mixed_list(lst):
    ret = []
    for i in lst:
        try:
            ret.append(int(i))
        except:
            ret.append(i)
    ret = sorted(ret, key=lambda x: (isinstance(x, str), x))
    return [str(i) for i in ret]

# Get listings
def stubhub_api(eventid):

    st = St(app_token,consumer_key,consumer_secret,stubhub_username,stubhub_password)

    df = pd.DataFrame(st.get_listings(eventid = eventid, pages=True))
    df = df.rename(spacer,axis='columns')
    return df


# Create Histogram
def create_hist(dff,column,title):
    return {
                'data':[go.Histogram(x = dff[column])],
                'layout': {'title': title}  
            }

# Create heatmap
def create_heatmap(dff,title):
    dff_price = pd.pivot_table(dff, values='listing Price', 
                     index=['section Name'], columns=['row'], 
                     aggfunc=np.mean)

    dff_quantity = pd.pivot_table(dff, values='quantity', 
                         index=['section Name'], columns=['row'], 
                         aggfunc=np.sum)

    dff = dff_price

    height = dff.shape[0]*15 
    if height < 400: height = 400

    cols = sort_mixed_list(list(dff.columns.values))
    dff = dff[cols]
    dff_quantity = dff_quantity[cols]

    x = ['(' + str(i) + ')' for i in dff.columns.values]
    y = dff.index
    z = dff.values.tolist()
    q = dff_quantity.values.tolist()

    hovertext = list()
    for yi, yy in enumerate(y):
        hovertext.append(list())
        for xi, xx in enumerate(x):
            hovertext[-1].append('''Row/Item: {}<br />Section: {}<br />Avg. Price: ${:,.2f}<br />Quantity: {:,.0f}'''
                                 .format(xx, yy, z[yi][xi],q[yi][xi]))


    trace = go.Heatmap(z = dff.values.tolist(),
                       y = y,
                       x = x,
                       hoverinfo='text',
                       text=hovertext,
                       colorscale='Viridis',
                       reversescale= True)

    layout = go.Layout(xaxis=dict(categoryorder='array', categoryarray=list(dff.columns.values), type="category", side="top"),
                       yaxis=dict(tickfont=dict(size=8)),
                       margin=go.Margin(l=200,r=50,b=100,t=150,pad=4),
                       height = height,
                       title = 'Average Price Per Seat by Section and Row/Item')
    # fig = go.Figure(data=[trace], layout=layout)
    return {
                'data':[trace],
                'layout': layout
            }

# Filter function
def filter_points(dff,selectedDatas):
        selectedids = dff.index
        for selected_data in selectedDatas:
            if selected_data is not None:
                selected_index = [p['pointNumbers'] for p in selected_data['points']]
                selected_index = sum(selected_index,[])
                selected_index = dff.iloc[selected_index].index
                if len(selected_index) > 0:
                    selectedids = np.intersect1d(
                        selectedids, selected_index)


        dff = dff.loc[dff.index.isin(selectedids),:]
        return selectedids

# submit button notification
@app.callback(dash.dependencies.Output('output-state', 'children'),
              [dash.dependencies.Input('submit-button', 'n_clicks'),
              dash.dependencies.Input('cache', 'children')],
              [dash.dependencies.State('input-1-state', 'value')])
def update_output(n_clicks,cache, input1):
    try:
        dff = pd.read_json(eval(cache), orient='split')
        retrieve_time = dff['retrieve Time'].iloc[0]
        return html.Div(['There are {} listings for event id {}.'.format(dff.shape[0], input1),
                         html.Br(),
                         'Data was retrieved on {}'.format(retrieve_time)])
    except:
        return 'Invalid event id.'

# fetch data suing stubhub api
@app.callback(dash.dependencies.Output('cache', 'children'),
              [dash.dependencies.Input('submit-button', 'n_clicks')],
              [dash.dependencies.State('input-1-state', 'value')])
def get_data(n_clicks, input1):
    dff = df
    if input1 != '': 
        dff = stubhub_api(input1)
        if dff is None:
            return json.dumps([None])
    return json.dumps(dff.to_json(orient='split'))

# Display Hist selection
# @app.callback(
#     dash.dependencies.Output('selected-data', 'children'),
#     [dash.dependencies.Input('g2', 'selectedData')])
# def display_selected_data(selectedDatas):
#     if selectedDatas is None: return
#     rows = [p['pointNumbers'] for p in selectedDatas['points']]
#     rows = sum(rows,[])
#     #points = filter_points(selectedDatas).index.values.tolist()

#     return json.dumps([selectedDatas], indent=2)


# create quantity histogram
@app.callback(dash.dependencies.Output('g1', 'figure'),
              [dash.dependencies.Input('cache', 'children')])
def create_quantity(data):
    dff = pd.read_json(eval(data), orient='split')
    return create_hist(dff,'quantity','Histogram of Ticket Quantity')

# create price histogram
@app.callback(dash.dependencies.Output('g2', 'figure'),
              [dash.dependencies.Input('cache', 'children')])
def create_price(data):
    dff = pd.read_json(eval(data), orient='split')
    return create_hist(dff,'listing Price','Histogram of Listing Price')

# create heatmap
@app.callback(dash.dependencies.Output('heatmap', 'figure'),
              [dash.dependencies.Input('cache', 'children'),
              dash.dependencies.Input('g1', 'selectedData'),
              dash.dependencies.Input('g2', 'selectedData')])
def generate_heatmap(data,*selectedDatas):
    dff = pd.read_json(eval(data), orient='split')
    #ind = filter_points(dff,selectedDatas)
    return create_heatmap(dff,'Avg Seat Price By Section and Row/Item')

# create and filter table
@app.callback(
dash.dependencies.Output('datatable-df', 'rows'),
[dash.dependencies.Input('cache', 'children'),
dash.dependencies.Input('g1', 'selectedData'),
dash.dependencies.Input('g2', 'selectedData')]
)
def create_table(cache,*selectedDatas):
    dff = pd.read_json(eval(cache), orient='split')
    ind = filter_points(dff,selectedDatas)
    return dff.iloc[ind].to_dict('records')

# download all listings button
@app.callback(
    dash.dependencies.Output('download-link', 'href'),
    [dash.dependencies.Input('datatable-df', 'selected_row_indices')])
def update_download_link(selected_row_indices):
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

# @app.callback(dash.dependencies.Output('tab-output', 'children'), 
#     [dash.dependencies.Input('tabs', 'value'),
#     dash.dependencies.Input('cache','children')])
# def display_tabs(value):
#     dash.dependencies.Input


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

# font awesome
app.css.append_css({
    'external_url': 'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css'
})

# Loading screen CSS
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

# google analytics 
app.scripts.append_script({
'external_url': 'https://www.googletagmanager.com/gtag/js?id=UA-116215073-1'
})

app.scripts.append_script({
'external_url': 'https://cdn.rawgit.com/KobaKhit/stuhub-listings/186dcc84/static/js/ga.js'
})




if __name__ == '__main__':
    app.run_server(debug=True)