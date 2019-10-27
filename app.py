import flask
import dash
import dash_html_components as html
import time

from flask import Flask, render_template,request
import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json

import pprint
import plotly.express as px
import subprocess

import threading

# app = Flask(__name__)



commands = {'zoom_in' : False, 'zoom_out' : False, 'swipe_right' : False, 'swipe_left' : False, 'swipe_up' : False, 'swipe_down' : False, 'idle': True, 'x':0, 'y':0}

def effect(inp):
    inp = inp.strip()
    for i in commands:
        commands[i] = True if i == inp else False
        print(i)
        print(inp)

server = flask.Flask(__name__)

@server.route('/')
def index():
    # return 'Hello Flask app'
    feature = 'Bar'
    bar = create_plot(feature)
    return render_template('index.html', plot=bar)


def create_plot(feature):
    if feature == 'Bar':
        N = 40
        x = np.linspace(0, 1, N)
        y = np.random.randn(N)
        df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe
        data = [
            go.Bar(
                x=df['x'], # assign x as the dataframe column 'x'
                y=df['y']
            )
        ]
    else:
        N = 1000
        random_x = np.random.randn(N)
        random_y = np.random.randn(N)

        # Create a trace
        data = [go.Scatter(
            x = random_x,
            y = random_y,
            mode = 'markers'
        )]


    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


@server.route('/bar', methods=['GET', 'POST'])
def change_features():

    feature = request.args['selected']
    graphJSON= create_plot(feature)


    return graphJSON


@server.before_first_request
def activate_job():
    """
    Runs before first request.
    Creates new thread for run_job()
    run_job is used to call a recurring background task
    Scrapes telo_lab at regular intervals in the background
    """
    def run_job():
        python2_path = "C:\\Python27\\python.exe"
        command = python2_path + " leapmotion.py"
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with process.stdout:
            print("nothing")
            for line in iter(process.stdout.readline, b''):
                print(line.decode())
                effect(line.decode())
    thread = threading.Thread(target=run_job)
    thread.start()


app = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dash/'
)


import dash_core_components as dcc

t = np.linspace(0, 10, 50)
x, y, z = np.cos(t), np.sin(t), t


iris = px.data.iris()
fig = px.scatter_3d(iris, x='sepal_length', y='sepal_width', z='petal_width',
              color='species')

camera = dict(
    up=dict(x=0, y=0, z=1),
    center=dict(x=0, y=0, z=0),
    eye=dict(x=1.25, y=1.25, z=1.25)
)

fig.update_layout(scene_camera=camera)


app.layout = html.Div([
    dcc.Input(id="input-2", type="number", value=2),
    dcc.Input(id="input-3", type="number", value=3),
    html.Div(id="number-output"),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'New York City', 'value': 'NYC'},
            {'label': 'Montreal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        value='NYC'
    ),
    # dcc.Graph(
    #     id='example-graph',
    #     figure={
    #         'data': [
    #             {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
    #             {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
    #         ],
    #         'layout': {
    #             'title': 'Dash Data Visualization'
    #         }
    #     }
    # )
    dcc.Graph(
        id='graph',
        config={
            'showSendToCloud': True,
            'plotlyServerURL': 'https://plot.ly'
        }
    ),
    dcc.Graph(
        id='graph2',
        figure=fig
    ),
    dcc.Interval(
            id='interval-component',
            interval=1*55, # in milliseconds
            n_intervals=0
        ),
    dcc.Input(id="input-1", type="number", value=1),

])


# @app.callback(
#     dash.dependencies.Output("input-1", "style"),
#     [dash.dependencies.Input("input-2", "value"), dash.dependencies.Input("input-3", "value")],
# )
# def update_output(input2, input3):
#     x = input2
#     y = input3
#     style = {
#         "padding": 0,
#         "width": "10px",
#         "height": "10px",
#         "border": "none",
#         "position": "fixed",
#         "left":x,
#         "top":y,
#         "background": "#000000",
#         "border-radius": "25px"

#     }
#     return style

# @app.callback(
#   dash.dependencies.Output('graph2', 'figure'),
#   [dash.dependencies.Input('interval-component', 'n_intervals')])
# def update_graph_pls(n):
#   f = fig
#   eye_dict['x'] -= 0.1
#   eye_dict['y'] -= 0.1
#   eye_dict['z'] -= 0.1
#   camera['eye'] = eye_dict
#   fig.update_layout(scene_camera=camera, title=name)
#   return f

theta = np.pi/80

@app.callback(
    [dash.dependencies.Output('graph2', 'figure'), dash.dependencies.Output("input-1", "style")],
    [dash.dependencies.Input('interval-component', 'n_intervals')],
    [dash.dependencies.State('graph2', 'figure')]
    )
def update_zoom(n, figure):
    temp_x = figure['layout']['scene']['camera']['eye']['x']
    temp_y = figure['layout']['scene']['camera']['eye']['y']
    temp_z = figure['layout']['scene']['camera']['eye']['z']
    old = np.array([temp_x, temp_y, temp_z])
    if commands['zoom_in'] or commands['zoom_out']:
        if commands['zoom_in']:
            figure['layout']['scene']['camera']['eye']['x'] -= 0.01
            figure['layout']['scene']['camera']['eye']['y'] -= 0.01
            figure['layout']['scene']['camera']['eye']['z'] -= 0.01
        elif commands['zoom_out']:
            figure['layout']['scene']['camera']['eye']['x'] += 0.01
            figure['layout']['scene']['camera']['eye']['y'] += 0.01
            figure['layout']['scene']['camera']['eye']['z'] += 0.01
    else:
        R = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        if commands['swipe_right']:
            # print(figure['layout']['scene']['camera'])
            R = np.array([
                [np.cos(-theta), -np.sin(-theta), 0],
                [np.sin(-theta), np.cos(-theta), 0],
                [0, 0, 1]
                ])
        elif commands['swipe_left']:
            R = np.array([
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta), np.cos(theta), 0],
                [0, 0, 1]
                ])
        if commands['swipe_up']:
            R = np.array([
                [np.cos(theta), 0, np.sin(theta)],
                [0, 1, 0],
                [-np.sin(theta), 0, np.cos(theta)]
                ])
        elif commands['swipe_down']:
            R = np.array([
                [np.cos(-theta), 0, np.sin(-theta)],
                [0, 1, 0],
                [-np.sin(-theta), 0, np.cos(-theta)]
                ])
        new = np.dot(R, old)
        figure['layout']['scene']['camera']['eye']['x'] = new[0]
        figure['layout']['scene']['camera']['eye']['y'] = new[1]
        figure['layout']['scene']['camera']['eye']['z'] = new[2]


    # print(n)
    # figure['layout']['scene']['camera']['eye']['x'] -= 0.01
    # figure['layout']['scene']['camera']['eye']['y'] -= 0.01
    # figure['layout']['scene']['camera']['eye']['z'] -= 0.01
    # if (n%10 == 0):
    #   pprint.pprint(figure)

    x = commands['x']
    y = commands['y']
    style = {
        "padding": 0,
        "width": "10px",
        "height": "10px",
        "border": "none",
        "position": "fixed",
        "left":x,
        "top":y,
        "background": "#000000",
        "border-radius": "25px"

    }
    return figure, style



@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('my-dropdown', 'value')])
def update_output(value):
    # zoom(camera, name)
    y_array_dict = {
        'NYC': [4,2,3],
        'MTL': [1, 2, 4],
        'SF': [5, 3, 6]
    }
    figs = {
        'data': [{
            'type': 'scatter',
            'y': y_array_dict[value]
        }],
        'layout': {
            'title': value
        }
    }
    # f = fig
    # camera = dict(
    #    up=dict(x=0, y=0, z=1),
    #    center=dict(x=0, y=0, z=0),
    #    eye=dict(x=1.25, y=1.25, z=1.25)
    # )
    # fig.update_layout(scene_camera=camera, title=name)
    # for i in range(10):
    #     camera["eye"]["x"] -= .1
    #     camera["eye"]["y"] -= .1
    #     camera["eye"]["z"] -= .1
    #     fig.update_layout(scene_camera = camera, title = name)

    return figs

if __name__ == '__main__':
    app.run_server(debug=True)
