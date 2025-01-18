import os
import dash
import json
import base64
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output
from tensorflow.keras.models import load_model
from svm_model import train_model, evaluate_model, visua_decision_boundary, evaluation_metrics
from dff_model import learning_curves_dff, confusion_matrix_dff, calculate_accuracy, block_topology, node_link_topology_with_neuron_weights, MODEL_PATH_DFF, HISTORY_PATH_DFF, EVAL_PATH_DFF

# File paths for saved artifacts
# MODEL_PATH_DFF = "dff_model.h5"
# HISTORY_PATH_DFF = "dff_training_history.json"
# EVAL_PATH_DFF = "dff_evaluation_metrics.json"
BLOCK_TOPOLOGY_PATH = "./model1/dff_model_topology.png"

def convert_image_to_base64(image_path):
    """
    Convert an image file to base64 format for embedding in Dash.
    """
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("SVM Decision Boundary Visualization"),
    html.H2("SVM Kernel: Linear"),
    html.Div([
        # Slider for parameter 'C'
        html.Div([
            html.Label("Adjust Regularization Parameter C:"),
            dcc.Slider(
                min=0, max=4,  # Logical range for even spacing
                marks={0: "0.01", 1: "0.1", 2: "1", 3: "5", 4: "10"},
                step=None,  # Restrict slider to only these values
                value=3,  # Default value: 1 (logical position 3)
                id='c-slider-linear'
            )
        ], style={'margin-bottom': '2px', 'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}),  # Add spacing below the slider

        # Container for decision boundary and evaluation metrics
        html.Div([
            dcc.Graph(id='decision-boundary-linear', style={'flex': '50%', 'margin-right': '1px'}),
            dcc.Graph(id='evaluation-metrics-linear', style={'flex': '50%'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'max-width': '1500px', 'margin': 'auto'})  # Graphs side by side
    ]),

    html.H2("SVM Kernel: Poly"),
    html.Div([
        # Slider for parameter 'C'
        html.Div([
            html.Label("Adjust Regularization Parameter C:"),
            dcc.Slider(
                min=0, max=4,  # Logical range for even spacing
                marks={0: "0.01", 1: "0.1", 2: "1", 3: "5", 4: "10"},
                step=None,  # Restrict slider to only these values
                value=3,  # Default value: 1 (logical position 3)
                id='c-slider-poly'
            )
        ], style={'margin-bottom': '2px', 'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}),  # Add spacing below the slider

        html.Div([
            html.Label("Adjust Degree:"),
            dcc.Slider(
                min=0, max=8,  # Logical range for even spacing
                marks={0: "2", 1: "3", 2: "4", 3: "5", 4: "6", 5: "7", 6: "8", 7: "9", 8: "10"},  # Define degree options
                step=None,  # Restrict slider to only these values
                value=1,  # Default value: 3
                id='degree-slider-poly'
            )
        ], style={'margin-bottom': '2px', 'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}),

        # Container for decision boundary and evaluation metrics
        html.Div([
            dcc.Graph(id='decision-boundary-poly', style={'flex': '50%', 'margin-right': '1px'}),
            dcc.Graph(id='evaluation-metrics-poly', style={'flex': '50%'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'max-width': '1500px', 'margin': 'auto'})  # Graphs side by side
    ]),

    html.H2("SVM Kernel: RBF"),
    html.Div([
        # Slider for parameter 'C'
        html.Div([
            html.Label("Adjust Regularization Parameter C:"),
            dcc.Slider(
                min=0, max=5,  # Logical range for even spacing
                marks={0: "0.01", 1: "0.1", 2: "1", 3: "5", 4: "10"},
                step=None,  # Restrict slider to only these values
                value=3,  # Default value: 1 (logical position 3)
                id='c-slider-rbf'
            )
        ], style={'margin-bottom': '2px', 'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}),  # Add spacing below the slider
        html.Div([
            html.Label("Adjust Gamma:"),
            dcc.Slider(
                min=0, max=3,  # Logical range for even spacing
                marks={0: "0.1", 1: "1", 2: "5", 3: "10"},
                step=None,  # Restrict slider to only these values
                value=2,  # Default value: 1
                id='gamma-slider-rbf'
            )
        ], style={'margin-bottom': '2px', 'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}),

        # Container for decision boundary and evaluation metrics
        html.Div([
            dcc.Graph(id='decision-boundary-rbf', style={'flex': '50%', 'margin-right': '1px'}),
            dcc.Graph(id='evaluation-metrics-rbf', style={'flex': '50%'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'max-width': '1500px', 'margin': 'auto'})  # Graphs side by side
    ]),

    html.H2("SVM Kernel: Sigmoid"),
    html.Div([
        # Slider for parameter 'C'
        html.Div([
            html.Label("Adjust Regularization Parameter C:"),
            dcc.Slider(
                min=0, max=4,  # Logical range for even spacing
                marks={0: "0.01", 1: "0.1", 2: "1", 3: "5", 4: "10"},
                step=None,  # Restrict slider to only these values
                value=3,  # Default value: 1 (logical position 3)
                id='c-slider-sigmoid'
            )
        ], style={'margin-bottom': '2px', 'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}),  # Add spacing below the slider

        # Container for decision boundary and evaluation metrics
        html.Div([
            dcc.Graph(id='decision-boundary-sigmoid', style={'flex': '50%', 'margin-right': '1px'}),
            dcc.Graph(id='evaluation-metrics-sigmoid', style={'flex': '50%'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'max-width': '1500px', 'margin': 'auto'})  # Graphs side by side
    ]),

    html.H1("Deep Feedforward Neural Network Visualization"),

    # Left column for DFF evaluation
    html.Div([
        html.H2("DFF Evaluation Metrics"),
        dcc.Graph(id="evaluation-metrics-dff", style={"height": "500px"}),  # Adjust height to fit well in the column

        html.H2("DFF Learning Curves"),
        dcc.Graph(id="learning-curves-dff", style={"height": "500px"}),

        html.H2("DFF Confusion Matrix"),
        dcc.Graph(id="confusion-matrix-dff", style={"width":"200", "height": "500px"}),

        # Topology
        html.H2("DFF Topology"),
        html.Img(id="topology-dff"),
    ], style={
        "width": "48%",       # Occupies 48% of the width
        "display": "inline-block",  # Side-by-side layout
        "vertical-align": "top",    # Aligns content to the top
        "padding-right": "10px"     # Adds spacing to the right
    }),

    # Right column for ... evaluation
    # html.Div([
    #     html.H2("DFF Evaluation Metrics"),
    #     dcc.Graph(id="evaluation-metrics-dff", style={"height": "500px"}),  # Adjust height to fit well in the column

    #     html.H2("DFF Learning Curves"),
    #     dcc.Graph(id="learning-curves-dff", style={"height": "500px"}),

    #     html.H2("DFF Confusion Matrix"),
    #     dcc.Graph(id="confusion-matrix-dff", style={"width":"200", "height": "500px"}),

    #     # Topology
    #     html.H2("DFF Topology"),
    #     html.Img(id="topology-dff"),
    # ], style={
    #     "width": "48%",       # Occupies 48% of the width
    #     "display": "inline-block",  # Side-by-side layout
    #     "vertical-align": "top",    # Aligns content to the top
    #     "padding-left": "10px"     # Adds spacing to the right
    # }),

    html.H2("DFF Topology"),
    dcc.Graph(id="node-topology-dff"),

])

# Linear SVM
@app.callback(
    [Output('decision-boundary-linear', 'figure'),
    Output('evaluation-metrics-linear', 'figure')],
    [Input('c-slider-linear', 'value')]
)
def update_plot(c_position):
    # Map slider position to actual C values
    c_values = [0.01, 0.1, 1, 5, 10]
    c = c_values[int(c_position)]

    x_min, x_max, y_min, y_max, Z, svc = train_model("linear", c)
    accuracy, precision, recall, f1 = evaluate_model(svc)
    decision_boundary_linear = visua_decision_boundary(x_min, x_max, y_min, y_max, Z)
    evaluation_metrics_linear = evaluation_metrics(accuracy, precision, recall, f1)
    return decision_boundary_linear, evaluation_metrics_linear

# Poly SVM
@app.callback(
    [Output('decision-boundary-poly', 'figure'),
    Output('evaluation-metrics-poly', 'figure')],
    [Input('c-slider-poly', 'value'),
    Input('degree-slider-poly', 'value')]
)
def update_plot(c_position, degree_position):
    # Map slider positions to actual C and degree values
    c_values = [0.01, 0.1, 1, 5, 10]
    degree_values = [2, 3, 4, 5, 6, 7, 8, 9, 10]  # Define degree options
    c = c_values[int(c_position)]
    degree = degree_values[int(degree_position)]

    x_min, x_max, y_min, y_max, Z, svc = train_model("poly", c, degree=degree) # degree should be changable
    accuracy, precision, recall, f1 = evaluate_model(svc)
    decision_boundary_poly = visua_decision_boundary(x_min, x_max, y_min, y_max, Z)
    evaluation_metrics_poly = evaluation_metrics(accuracy, precision, recall, f1)
    return decision_boundary_poly, evaluation_metrics_poly

# RBF SVM
@app.callback(
    [Output('decision-boundary-rbf', 'figure'),
    Output('evaluation-metrics-rbf', 'figure')],
    [Input('c-slider-rbf', 'value'),
    Input('gamma-slider-rbf', 'value')]
)
def update_plot(c_position, gamma_position):
    # Map slider positions to actual C and gamma values
    c_values = [0.01, 0.1, 1, 5, 10]
    gamma_values = [0.1, 1, 5, 10]
    c = c_values[int(c_position)]
    gamma = gamma_values[int(gamma_position)]

    x_min, x_max, y_min, y_max, Z, svc = train_model("rbf", c, gamma=gamma) # gamma should be changable
    accuracy, precision, recall, f1 = evaluate_model(svc)
    decision_boundary_rbf = visua_decision_boundary(x_min, x_max, y_min, y_max, Z)
    evaluation_metrics_rbf = evaluation_metrics(accuracy, precision, recall, f1)
    return decision_boundary_rbf, evaluation_metrics_rbf

# Sigmoid SVM
@app.callback(
    [Output('decision-boundary-sigmoid', 'figure'),
    Output('evaluation-metrics-sigmoid', 'figure')],
    [Input('c-slider-sigmoid', 'value')]
)
def update_plot(c_position):
    c_values = [0.01, 0.1, 1, 5, 10]
    c = c_values[int(c_position)]
    x_min, x_max, y_min, y_max, Z, svc = train_model("sigmoid", c, gamma=2, degree=3)
    accuracy, precision, recall, f1 = evaluate_model(svc)
    decision_boundary_sigmoid = visua_decision_boundary(x_min, x_max, y_min, y_max, Z)
    evaluation_metrics_sigmoid = evaluation_metrics(accuracy, precision, recall, f1)
    return decision_boundary_sigmoid, evaluation_metrics_sigmoid

# DFF
@app.callback(
    [Output("evaluation-metrics-dff", "figure"),
    Output("learning-curves-dff", "figure"),
    Output("confusion-matrix-dff", "figure")],
    [Input("learning-curves-dff", "id")]  # A dummy input to trigger the callback once
)
def update_graphs(_):

    # Load training history
    with open(HISTORY_PATH_DFF, 'r') as f:
        history = json.load(f)
    # Load evaluation metrics
    with open(EVAL_PATH_DFF, 'r') as f:
        evaluation = json.load(f)
    conf_matrix = np.array(evaluation["confusion_matrix"])
    classification_report = evaluation["classification_report"]

    # Calculate accuracy from the confusion matrix
    accuracy = calculate_accuracy(conf_matrix)

    # Extract weighted averages for precision, recall, and F1-score
    precision = classification_report["weighted avg"]["precision"]
    recall = classification_report["weighted avg"]["recall"]
    f1 = classification_report["weighted avg"]["f1-score"]

    # Generate visualizations
    evaluation_metrics_dff = evaluation_metrics(accuracy, precision, recall, f1)
    learning_curves_fig_dff = learning_curves_dff(history)
    confusion_matrix_fig_dff = confusion_matrix_dff(conf_matrix)
    

    return  evaluation_metrics_dff, learning_curves_fig_dff, confusion_matrix_fig_dff

@app.callback(
    [Output("topology-dff", "src"),
    Output("node-topology-dff", "figure")],
    [Input("learning-curves-dff", "id")]  # A dummy input to trigger the callback once
)
def update_graphs(_):
    
    # Generate and encode topology diagram
    topology_image_path = block_topology(MODEL_PATH_DFF, BLOCK_TOPOLOGY_PATH)
    with open(topology_image_path, "rb") as img_file:
        block_topology_dff = "data:image/png;base64," + base64.b64encode(img_file.read()).decode()

    node_link_topology_fig = node_link_topology_with_neuron_weights(MODEL_PATH_DFF)

    return  block_topology_dff, node_link_topology_fig



# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)