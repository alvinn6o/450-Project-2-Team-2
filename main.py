import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

from pie import create_pie_chart, CATEGORY_ORDER, COLOR_MAP, delay_label_map

#Load and prepare data
df = pd.read_csv("airline_delay.csv")

#Handle missing values before computing metrics
count_cols = ["arr_flights", "carrier_ct", "weather_ct", "nas_ct", "security_ct", "late_aircraft_ct"]
time_cols = ["arr_delay", "arr_del15"]

#Fill count-based columns with mode (most frequent value)
for col in count_cols:
    if df[col].isna().any():
        mode_val = df[col].mode()[0]
        df[col].fillna(mode_val, inplace=True)

#Fill time-based columns with median
for col in count_cols:
    if df[col].isna().any():
        median_val = df[col].median()
        df[col].fillna(median_val, inplace=True)

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
            value=["All"],
            multi=True, #added for multi-selection
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
            value=["All"],
            multi=True, #multi-selection
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
            value=["All"],
            multi=True,
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
            value=["All"],
            multi=True,
            clearable=False,
        ),
    ], style={"width": "22%", "display": "inline-block"}),

    html.Div([
        html.Label("View Mode:"),
        dcc.RadioItems(
            id="view-mode",
            options=[
                {"label": "All Delay Causes", "value": "all"},
                {"label": "Dominant Delay Cause", "value": "dominant"}
            ],
            value="all",
            inline=True
        )
    ], style={"margin-top": "15px"}),

    dcc.Graph(id="delay-scatter", style={"margin-top": "20px"}),
    dcc.Graph(id="delay-pie", style={"margin-top": "20px"})
])

#display text function for filters below
def format_selection(selection, label):
    if "All" in selection:
        return f"All {label}s"
    return ", ".join(map(str, selection))

#Update scatterplot
@app.callback(
    Output("delay-scatter", "figure"),
    Output("delay-pie", "figure"),
    Input("year-dropdown", "value"),
    Input("carrier-dropdown", "value"),
    Input("state-dropdown", "value"),
    Input("delay-dropdown", "value"),
    Input("view-mode", "value")
)
def update_scatter(selected_year, selected_carrier, selected_state, selected_delay, view_mode):
    filtered = df_melted.copy()

    if "All" not in selected_year:
        filtered = filtered[filtered["year"].isin(selected_year)]

    if "All" not in selected_carrier:
        filtered = filtered[filtered["carrier_name"].isin(selected_carrier)]

    if "All" not in selected_state:
        filtered = filtered[filtered["state"].isin(selected_state)]

    if "All" not in selected_delay:
        filtered = filtered[filtered["delay_type"].isin(selected_delay)]

    # Map delay types to readable labels
    filtered["delay_type"] = filtered["delay_type"].map(delay_label_map)

    # Compute percentage of delayed flights
    filtered["delay_percent"] = (filtered["total_delays"] / filtered["arr_flights"]) * 100
    filtered["delay_percent_label"] = filtered["delay_percent"].round(3).astype(str) + "%"

    filtered["delay_share"] = (filtered["delay_count"] / filtered["total_delays"]) * 100
    filtered["delay_share_label"] = filtered["delay_share"].round(2).astype(str) + "%"

    #Show dominant delay if toggle is set
    if view_mode == "dominant":
        dominant = (
            filtered.groupby(
                ["airport_name", "year", "state", "carrier_name", "arr_flights", "on_time_percent", "total_delays", "arr_delay"],
                as_index=False
            )
            .apply(lambda g: g.loc[g["delay_count"].idxmax()])
            .reset_index(drop=True)
        )
        filtered = dominant

    #names for chart
    year_txt = format_selection(selected_year, "Year")
    carrier_txt = format_selection(selected_carrier, "Carrier")
    state_txt = format_selection(selected_state, "State")
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

    if "All" in selected_delay:
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
        size="delay_percent",
        hover_data=["carrier_name", "airport_name", "state", "year", "delay_type", "arr_flights", "on_time_percent", "delay_count", "delay_percent_label", "arr_delay", "total_delays", "delay_share_label"],
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
            "delay_percent_label": "Delayed Flights (%)",
            "delay_count": "Delayed Flights (count)",
            "total_delays": "Total Delays",
            "arr_delay": "Average Arrival Delay (min)",
            "year": "Year",
            "state": "State",
            "airport_name": "Airport",
            "delay_type": "Delay Cause",
            "carrier_name": "Carrier",
            "delay_share_label": "Share of Total Delays (%)"
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
