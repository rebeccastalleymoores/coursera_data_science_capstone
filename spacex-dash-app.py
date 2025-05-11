# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Rename 'class' column to avoid conflict with reserved keyword
spacex_df['launch_status'] = spacex_df['class'].map({1: 'Successful', 0: 'Unsuccessful'})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] +
                                            [{'label': site, 'value': site} for site in
                                             spacex_df['Launch Site'].unique()],
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div([
                                    dcc.Graph(id='success-pie-chart'),
                                    html.Br(),
                                    html.P("Payload range (Kg):"),
                                    dcc.RangeSlider(
                                        id='payload-slider',
                                        min=0,
                                        max=10000,
                                        step=1000,
                                        marks={i: str(i) for i in range(int(min_payload), int(max_payload), 1000)},
                                        value=[min_payload, max_payload]
                                    )
                                ]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        # Group by Launch Site and sum the 'class' column (which contains 1 for success)
        success_counts = spacex_df.groupby('Launch Site')['launch_status'].value_counts().unstack().fillna(
            0).reset_index()
        success_counts['Total'] = success_counts['Successful'] + success_counts['Unsuccessful']
        fig = px.pie(
            success_counts,
            names='Launch Site',
            values='Successful',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count successes and failures
        success_counts = filtered_df['launch_status'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        fig = px.pie(
            success_counts,
            names='class',
            values='count',
            title=f'Success vs. Failure for {entered_site}'
        )
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def get_scatter_plot(entered_site, payload_range):
    min_payload, max_payload = payload_range

    # Filter by payload range
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(min_payload, max_payload)]

    if entered_site != 'ALL':
        # Further filter by launch site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    # Create scatter plot using numeric class column
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Successful Launches by Payload for {entered_site}' if entered_site != 'ALL'
        else 'Total Successful Launches by Payload',
        labels={'class': 'Launch Outcome'}
    )

    # Fix y-axis labels so they show "Unsuccessful" and "Successful"
    fig.update_yaxes(
        tickvals=[0, 1],
        ticktext=['Unsuccessful', 'Successful']
    )

    return fig




# Run the app
if __name__ == '__main__':
    app.run(debug=True)
