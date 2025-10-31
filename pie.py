import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

delay_label_map = {
    "carrier_ct": "Carrier Delay",
    "weather_ct": "Weather Delay",
    "nas_ct": "NAS Delay",
    "security_ct": "Security Delay",
    "late_aircraft_ct": "Late Aircraft Delay"
}

CATEGORY_ORDER = [
    "Carrier Delay",
    "Weather Delay",
    "NAS Delay",
    "Security Delay",
    "Late Aircraft Delay",
]

COLOR_MAP = {
    "Carrier Delay": "#636EFA",
    "Weather Delay": "#00CC96",
    "NAS Delay": "#EF553B",
    "Security Delay": "#AB63FA",
    "Late Aircraft Delay": "#FFA15A",
}


def create_pie_chart(df: pd.DataFrame, title: str = "Proportion of Delay Types"):


    if df is None or df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title=title,
            template="plotly_white",
            annotations=[{
                'text': 'No data available',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5, 'y': 0.5,
                'showarrow': False,
                'font': {'size': 16}
            }]
        )
        return empty_fig
    
    df_pie = df.copy()

    # Group by delay_type and sum delay counts
    df_pie = (
        df_pie.groupby("delay_type", as_index=False)["delay_count"]
        .sum()
    )


    if df_pie["delay_count"].sum() == 0:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title=title,
            template="plotly_white",
            annotations=[{
                'text': 'No delays recorded',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5, 'y': 0.5,
                'showarrow': False,
                'font': {'size': 16}
            }]
        )
        return empty_fig
    
    fig = px.pie(
        df_pie,
        values="delay_count",
        names="delay_type",
        title=title,
        color="delay_type",
        color_discrete_map=COLOR_MAP,
        category_orders={"delay_type": CATEGORY_ORDER}
    )

    fig.update_traces(textposition="inside", textinfo="percent+label", 
                      hovertemplate="%{label}: %{value} delays (%{percent})<extra></extra>")
    
    fig.update_layout(
        template="plotly_white",
        legend_title_text="Delay Types"
    )

    return fig