import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

from pie import create_pie_chart, CATEGORY_ORDER, COLOR_MAP, delay_label_map

#Load and prepare data
df = pd.read_csv("airline_delay.csv")

#Extracting States
df["state"] = df["airport_name"].str.extract(r",\s*([A-Z]{2})")
df["state"] = df["state"].fillna("Unknown")

#Compute metrics
df["total_delays"] = df[["carrier_ct",  "weather_ct", "nas_ct", "security_ct", "late_aircraft_ct"]].sum(axis=1)
df["on_time_percent"] = (1 - (df["arr_del15"] / df["arr_flights"])) * 100

#Drop rows missing key data
df = df.dropna(subset=["arr_flights", "on_time_percent", "carrier_name", "year"])

#Melted delay_type column
delay_cols = ["carrier_ct", "weather_ct", "nas_ct", "security_ct", "late_aircraft_ct"]
df_melted = df.melt(
    id_vars=["year", "carrier_name", "airport_name", "state", "arr_flights", "on_time_percent", "total_delays", "arr_delay"],
    value_vars=delay_cols,
    var_name="delay_type",
    value_name="delay_count"
)

#Starting Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H2("Flight Delay Analysis"),

    #Year dropdown menu
    html.Div([
            html.Label("Select Year:"),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": str(y), "value": y} for y in sorted(df["year"].unique())],
                value="All",
                clearable=False,
            ),
    ], style={"width": "22%", "display": "inline-block", "margin-right": "1%"}),

    #Carrier dropdown menu
    html.Div([
            html.Label("Select Carrier:"),
            dcc.Dropdown(
                id="carrier-dropdown",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": str(y), "value": y} for y in sorted(df["carrier_name"].unique())],
                value="All",
                clearable=False,
            ),
    ], style={"width": "22%", "display": "inline-block", "margin-right": "1%"}),

    #State dropdown menu
    html.Div([
            html.Label("Select State:"),
            dcc.Dropdown(
                id="state-dropdown",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": str(y), "value": y} for y in sorted(df["state"].unique())],
                value="All",
                clearable=False,
            ),
    ], style={"width": "22%", "display": "inline-block", "margin-right": "1%"}),

    #Delay Cause dropdown menu
    html.Div([
        html.Label("Select Delay Cause:"),
        dcc.Dropdown(
            id="delay-dropdown",
            options=[
                {"label": "All", "value": "All"},
                {"label": "Carrier Delays", "value": "carrier_ct"},
                {"label": "Weather Delays", "value": "weather_ct"},
                {"label": "NAS Delays", "value": "nas_ct"},
                {"label": "Security Delays", "value": "security_ct"},
                {"label": "Late Aircraft Delays", "value": "late_aircraft_ct"},
            ],
            value="All",
            clearable=False,
        ),
    ], style={"width": "22%", "display": "inline-block"}),

    dcc.Graph(id="delay-scatter", style={"margin-top": "20px"}),

    dcc.Graph(id="delay-pie", style={"margin-top": "20px"})
])

#Update scatterplot
@app.callback(
    Output("delay-scatter", "figure"),
    Output("delay-pie", "figure"),
    Input("year-dropdown", "value"),
    Input("carrier-dropdown", "value"),
    Input("state-dropdown", "value"),
    Input("delay-dropdown", "value"),
)
def update_scatter(selected_year, selected_carrier, selected_state, selected_delay):

    filtered = df_melted.copy()

        # Apply filters
    if selected_year != "All":
        filtered = filtered[filtered["year"] == selected_year]
    if selected_carrier != "All":
        filtered = filtered[filtered["carrier_name"] == selected_carrier]
    if selected_state != "All":
        filtered = filtered[filtered["state"] == selected_state]
    if selected_delay != "All":
        filtered = filtered[filtered["delay_type"] == selected_delay]

    # Map delay types to readable labels
    filtered["delay_type"] = filtered["delay_type"].map(delay_label_map)


    year_txt = "All Years" if selected_year == "All" else str(selected_year)
    carrier_txt = "All Carriers" if selected_carrier == "All" else str(selected_carrier)
    state_txt = "All States" if selected_state == "All" else str(selected_state)
    pie_title = f"Delay Cause Breakdown — {carrier_txt}, {state_txt}, {year_txt}"
    pie_fig = create_pie_chart(filtered, title=pie_title)

    filtered["delay_type"] = pd.Categorical(
        filtered["delay_type"],
        categories=[
            "Carrier Delay",
            "Weather Delay",
            "NAS Delay",
            "Security Delay",
            "Late Aircraft Delay"
        ],
        ordered=False
    )

    if selected_delay == "All":
        jitter_strength_x = 50
        jitter_strength_y = 0.3
        filtered["arr_flights"] = filtered["arr_flights"] + np.random.uniform(-jitter_strength_x, jitter_strength_x, len(filtered))
        filtered["on_time_percent"] = filtered["on_time_percent"] + np.random.uniform(-jitter_strength_y, jitter_strength_y, len(filtered))
        filtered["on_time_percent"] = filtered["on_time_percent"].clip(0, 100)


    # Scatter plot
    fig = px.scatter(
        filtered,
        x="arr_flights",
        y="on_time_percent",
        color="delay_type",
        size="delay_count",
        hover_data=["airport_name", "year", "state", "total_delays", "arr_delay"],
        title="On-Time Arrival Rate vs Total Flights",
        color_discrete_map=COLOR_MAP,
        category_orders={"delay_type": [
            "Carrier Delay",
            "Weather Delay",
            "NAS Delay",
            "Security Delay",
            "Late Aircraft Delay"
        ]},
        labels={
            "arr_flights": "Total Flights",
            "on_time_percent": "On-Time Arrival Rate (%)",
            "delay_count": "Delay Count",
            "total_delays": "Total Delays",
            "arr_delay": "Average Arrival Delay (min)",
            "year": "Year",
            "state": "State",
            "airport_name": "Airport",
            "delay_type": "Delay Cause"
        }
    )

    fig.update_traces(marker=dict(opacity=0.7, line=dict(width=0)))

    # Layout styling
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Total Flights (Count)",
        yaxis_title="On-Time Arrival Rate (%)",
        legend_title_text="Delay Type",
        legend=dict(
            orientation="v",
            x=1.02,
            y=1,
            bgcolor="rgba(255,255,255,0)",
            bordercolor="LightGray",
            borderwidth=1
        ),
        margin=dict(l=60, r=40, t=80, b=60)
    )

    return fig, pie_fig

if __name__ == "__main__":
    app.run(debug=False)