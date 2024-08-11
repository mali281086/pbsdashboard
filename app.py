import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px


# Read the excel file to ingest data into DataFrame
df = pd.read_excel('PBS Data.xlsx', sheet_name='commodities_final')
df_forex = pd.read_excel('PBS Data.xlsx', sheet_name='forex')
# Dropping unnecessary columns
# df = df.drop(['Description', 'Unit', 'Price'], axis=1)

# Calculate percentage change on Price_Unit
df['Growth'] = df.groupby(['City', 'Product'])['Price_Unit'].pct_change() * 100

# Formatting columns
df['Date'] = pd.to_datetime(df['Date'])
df_forex['Date'] = pd.to_datetime(df_forex['Date'])
df['Price_Unit'] = df['Price_Unit'].apply(float).round(2)
df['Growth'] = df['Growth'].apply(float).round(2)

# Extract Year and Month Name
df['Year'] = df['Date'].dt.year
df_forex['Year'] = df_forex['Date'].dt.year
df['Month'] = df['Date'].dt.strftime('%b')

app = Dash(__name__)
server = app.server

# Creating the filters / selectors
city_dropdown = dcc.Dropdown(
    options=df['City'].unique(),
    value=['Karachi'],
    multi=True,
    id='city_dropdown_id'
)

product_dropdown = dcc.Dropdown(
    options=df['Product'].unique(),
    value=['Beef'],
    multi=True,
    id='product_dropdown_id'
)

year_slider = dcc.RangeSlider(
    df['Year'].min(),
    df['Year'].max(),
    step=None,
    value=[df['Year'].min(),
           df['Year'].max()],
    tooltip={"placement": "bottom","always_visible": True},
    id='year_slider_id',
    marks={str(year): str(year) for year in df['Year'].unique()}
)

app.layout = html.Div(style={'background-color': '#ffffff', 'margin': '0', 'padding': '0'}, children=[
    html.H1(children='Commodity Price Index'),
    html.Div([
        html.Div([
            html.Label(children='City'),
            city_dropdown
        ], style={'width': '48%', 'display': 'inline-block', 'margin-right': '0.5%'}),  # Adjust width as needed

        html.Div([
            html.Label(children='Commodity'),
            product_dropdown
        ], style={'width': '48%', 'display': 'inline-block'})  # Adjust width as needed
    ]),
    html.Hr(),
    html.Label(children='Year Slider'),
    year_slider,
    html.Hr(),
    html.Div([
        html.Div([
            html.H6(children='USD/PKR Trend'),
            dcc.Graph(id='forex_index', config={'displayModeBar': False})],
                 style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.H6(children='Commodity Price Trend'),
            dcc.Graph(id='commodity_price_index', config={'displayModeBar': False})],
                 style={'width': '48%', 'display': 'inline-block', 'margin-right': '0.5%'})
    ]),
    html.Hr(),  
        html.Div([
            html.H6(children='Correlation between USD/PKR and Commodity Price'),
            dcc.Graph(id='correlation_index', config={'displayModeBar': False})],
                 style={'width': '100%', 'display': 'inline-block'})
])


@app.callback(
    Output(component_id='commodity_price_index', component_property='figure'),
    Output(component_id='forex_index', component_property='figure'),
    Output(component_id='correlation_index', component_property='figure'),  # Add this line
    Input(component_id='city_dropdown_id', component_property='value'),
    Input(component_id='product_dropdown_id', component_property='value'),
    Input(component_id='year_slider_id', component_property='value')
)

def update_graph(city_param, product_param, year_param):
    dff = df[(df['Year'].between(min(year_param), max(year_param))) & (df['City'].isin(city_param)) & (df['Product'].isin(product_param))]

    commodity_fig = px.line(dff,
                            x='Date',
                            y='Price',
                            color='City',
                            line_dash='Product',
                            title=f'Government Issued Price Index for {product_param} in {city_param}')

    commodity_fig.update_xaxes(title='Year')
    commodity_fig.update_yaxes(title='Price')

    dff2 = df_forex[(df_forex['Year'].between(min(year_param), max(year_param)))]

    currency_fig = px.line(dff2,
                           x='Date',
                           y='USDPKR')

    currency_fig.update_xaxes(title='Year')
    currency_fig.update_yaxes(title='USD/PKR')

    # Calculate correlation between USD/PKR and selected commodity's price
    correlation_data = dff.merge(dff2, on='Date', how='inner')
    # Calculate the average price for selected products date-wise
    correlation_data['Average_Price'] = correlation_data.groupby(['Date'])['Price'].transform('mean')

    correlation = correlation_data['Average_Price'].corr(correlation_data['USDPKR']) * 100

    # Create correlation graph
    correlation_graph = px.line(correlation_data, x='Date', y=['Average_Price', 'USDPKR'], title=f'Correlation: {correlation:.2f}%')

    return commodity_fig, currency_fig, correlation_graph
# Following lines can be added if we want to create a input page separately and view the chart.
#     line_fig.show(config=dict(displayModeBar=False)
#     )

if __name__ == '__main__':
    app.run_server(debug=True)