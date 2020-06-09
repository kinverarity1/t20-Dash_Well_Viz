import dash
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
import pandas as pd

from welly import Well

from dashwellviz.figures import make_composite_log, draw_strat, draw_lith

# PREPARE DATA

logs = Well.from_las("Data/6628-21945_well_logs.las").df()

# For stratigraphy, make a pandas DataFrame with columns "depth_from", "depth_to", "label"
strat = pd.read_csv("Data/6628-21945_stratigraphy.csv").rename(
    columns={
        "unit_depth_from": "depth_from",
        "unit_depth_to": "depth_to",
        "strat_name": "label",
    }
)
if not "colour" in strat:
    strat["colour"] = None
strat = strat[["depth_from", "depth_to", "label", "colour"]]

# Make a dataframe with columns depth_from, depth_to, class, and label -- colours are determined by class
# class can be null/NaN for unclassifiable intervals
lith = pd.read_csv("Data/6628-21945_lithology.csv").rename(
    columns={"major_lith_code": "class", "Description": "label"}
)
if not "colour" in lith:
    lith["colour"] = None
lith = lith[["depth_from", "depth_to", "class", "label", "colour"]]

# CREATE APP

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.Div(
            className="app-header",
            children=[
                html.Div(
                    className="header",
                    children=[
                        html.Div(
                            className="logo_txt",
                            children=[
                                html.Img(
                                    src="./assets/img/swung_round_no_text.png",
                                    height="75px",
                                    className="logo_img",
                                ),
                                html.Div(
                                    "Template", className="app-header--title"
                                ),
                            ],
                        ),
                        html.Div(
                            className="project-subtitle",
                            children=["A Transform 2020 Project"],
                        ),
                    ],
                )
            ],
        ),
        html.Div(
            className="page",
            children=[
                html.Div(
                    className="sidebar",
                    children=[
                        html.H1("Sidebar"),
                        dcc.Dropdown(
                            id="mnemonic-selector",
                            options=[
                                {"label": key, "value": key} for key in logs.keys()
                            ],
                            value=[],
                            multi=True,
                        ),
                        html.Pre(id="debug-output")
                    ],
                ),
                html.Div(
                    className="well-plot-container",
                    children=[
                        html.H1("Well Plots Can Go Here"),
                        dcc.Graph(id="log-plot"),
                    ],
                ),
                html.Div(
                    className="other-plot-container",
                    children=[
                        html.H1("Other Plots Can Go Here"),
                        dcc.Graph(id="strat-lith-plots"),
                    ],
                ),
            ],
        ),
    ]
)



@app.callback(
    dash.dependencies.Output('log-plot', 'figure'),
    [dash.dependencies.Input('mnemonic-selector', 'value')])
def mnemonic_selection_changed(mnemonics):
    if len(mnemonics) > 0:
        log = make_composite_log(logs, lines=[[curve] for curve in mnemonics])
        return log.fig
    else:
        return go.Figure()

if __name__ == "__main__":
    app.run_server(debug=True)
