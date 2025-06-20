import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Charger les données
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Créer l'application Dash
app = dash.Dash(__name__)

# Liste des sites (corrigée selon le contenu réel du fichier CSV)
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site}
    for site in spacex_df['Launch Site'].unique()
]

# Définir la mise en page de l'application
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),

    # Dropdown pour sélectionner un site
    dcc.Dropdown(id='site-dropdown',
                 options=site_options,
                 value='ALL',
                 placeholder='Select a Launch Site here',
                 searchable=True),
    html.Br(),

    # Graphique circulaire (Pie Chart)
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # RangeSlider pour la masse du payload
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000',
                           7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]),
    html.Br(),

    # Graphique de dispersion (Scatter Chart)
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback pour mettre à jour le pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(site):
    if site == 'ALL':
        fig = px.pie(spacex_df, values='class', names='Launch Site',
                     title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == site]
        counts = filtered_df['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']
        counts['class'] = counts['class'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(counts, values='count', names='class',
                     title=f'Success vs. Failure for {site}')
    return fig

# Callback pour mettre à jour le scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(site, payload_range):
    low, high = payload_range
    df_filtered = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if site != 'ALL':
        df_filtered = df_filtered[df_filtered['Launch Site'] == site]

    fig = px.scatter(df_filtered,
                     x='Payload Mass (kg)',
                     y='class',
                     color='Booster Version Category',
                     title='Payload vs. Outcome for All Sites' if site == 'ALL'
                     else f'Payload vs. Outcome for {site}')
    return fig

# Lancer le serveur Dash
if __name__ == '__main__':
    print("🚀 Application Dash en cours de lancement...")
    app.run(port=8060)
