# 450-Project-2-Team-2

**Presentation Slides**

[**Original Visualization Notebook**](https://www.kaggle.com/code/chibss/aeroguard-flight-delay-cause-analysis/notebook)

## Original Visualization
- The originial visualization is a scatterplot in the **AeroGuard: Flight Cause Analysis** Kaggle notebook linked above.
  - Collection of visualizations aiming to identify the causes of flight delays in the airline industry with data from 2019-2020
- Scatterplot visualizes the relationship between departure delays and arrival delays
- Seeks to analyze whether departure delays contribute to arrival delays across airports and identify potential systemic inefficiencies in airport operations
- Shows a clear positive correlation where airports with high departure delays often have higher arrival delays.

## Dataset Used
- airline_delay.csv based on US Department of Transportation (DOT) and Bureau of Transportation Statistic (BTS) Data from 2019-2020
- Structure:
  - Rows: Combination of airport-carrier-month info
  - Columns: Flight totals, delay counts, and categorized delay causes by DOT/BTS standards.
- **Temporal Data**: year, month
- **Carrier Info**: carrier, carrier_name
- **Airport Info**: airport_name, arr_flights (number of arriving flights)
- **Delay Counts**: arr_del15 (flights delayed more than 15 minutes), carrier_ct, weather_ct, nas_ct, security_ct, late_aircraft_ct
- **Delay Outcomes**: arr_cancel, arr_diverted, arr_delay (total delay minutes)
- **Delay Duration (minutes)**: carrier_delay, weather_delay, nas_delay, security_delay, late_aircraft_delay

## Original Visualization Limitations
- Narrow Scope
  - Shows correlation between departure and arrival delays but doesn’t show underlying reasons for delays in the same view.
- Isolated Views
  - While notebook includes other visuals explaining delay causes, they’re not connected to this scatterplot, making it difficult to see how causes contribute to this pattern
- Lack of Interactivity
  - Visual is static, so users can’t interact with the visual (i.e. zoom, hover tooltips, filter, etc.), limiting deeper analysis.
- Visual Overlap
  - Points cluster heavily near lower delay values, making it difficult to distinguish between airports highlighted there.
- Missed Opportunity for Integration
  - Scatterplot and other charts function separately instead of combining insights at the instance (airport) and category (cause) levels.
 
## Improvement Goals
- **Main Goal**: Our goal with this visualization is to answer more in depth questions about flight delays from the year 2020. The kinds of questions we would want to answer are which airline has the most delays in a specific month by which type of delay. The previous visualization using this data could show which airline had the most delays, but would not be able to get into specific details. 
- Shift Analytical Focus
  - Shift focus to examining on-time arrival rate vs. total flights, providing a clearer picture of how carrier volume affects punctuality.
- Unify Correlation and Cause Analysis
  - Connect the scatterplot’s operational metrics with the notebook’s delay-cause insights, allowing users to see what delay causes influence which performance patterns.
- Enhance Interactivity
  - Add dynamic dropdown filters allowing users to explore data from multiple perspectives and isolate specific trends.
- Link Multiple Views for Context
  - Combine the scatterplot and pie chart so that user selections automatically update both, connecting insights between flights and delay causes.
- Enable Comparative Analysis
  - Move from static charts to a multi-view interactive dashboard unifying the insights presented in the notebook.

## Design/Features
- Hybrid Visualization
  - Combines a scatterplot and pie chart to connect delay correlations with delay cause composition
  - Users can see and update both visualizations simultaneously 
- Interactive Features
  - Hover tooltips and dynamic filtering using dropdown menus for Year, Carrier, State, and Delay Cause to enable targeted analysis
  - Added toggle for viewing dominant delay causes
- Improved Encodings and Readability
  - X-axis: Total Flights
  - Y-axis: On time arrival rate
  - Bubble size: Percentage of delayed flights
  - Color: Delay type (Carrier, Weather, NAS, Security, Late Aircraft)

## Libraries Used
- **Pandas**: Loading, cleaning, and transforming the dataset
- **Numpy**: Numeric operations and adding jitter to dense data points for enhanced readability
- **Plotly Express**: Building interactive scatterplot with color, size, and hover encodings
  - Plotly Graph Objects: Fine-tuning chart appearance and legends
- **Dash**: Creating layouts and dropdowns as well as handling dynamic visual update via callbacks

## Setup and Run Instructions
1. Install dependencies pip install pandas plotly dash
2. Make sure all files are in same folder as main.py
4. Run the app python main.py
5. Open in your browser Visit: http://127.0.0.1:8050/ (Should appear in your console window)



