from flask import Flask, render_template, jsonify, request, Response
from waitress import serve
from .api import AstrAPI
from .utils import suffix
import sys, json

def debug(head, *args):
    print (head, *args, file=sys.stderr)
    return head

app = Flask(__name__)

app.debug = True

api_route_options = {
    'version': 'v1'
}

def api_route(path, *args, **kwargs):
    path = ("/api/{version}/" + path).format(**api_route_options)
    debug ("[API] route created: " + path)
    return app.route(path, **kwargs)

@api_route('chart_placements', methods = ['POST'])
def chart_placements():
    return AstrAPI.handle('chart_placements')

@api_route('chart_houses', methods = ['POST'])
def chart_houses():
    return AstrAPI.handle('chart_houses')

@api_route('chart_aspects', methods = ['POST'])
def chart_aspects():
    return AstrAPI.handle('chart_aspects')

@api_route('natal_report', methods = ['POST'])
def natal_report():
    return AstrAPI.handle('natal_report')

@api_route('natal_report_html', methods = ['POST'])
def natal_report_html():
    return AstrAPI.handle('natal_report_html')

@api_route('calcul_aspect', methods = ['POST'])
def calcul_aspect():
    return AstrAPI.handle('calcul_aspect')

for resource, params in AstrAPI.RESOURCES.items():
    @api_route(resource, methods = ['POST', 'GET', 'DELETE'])
    @suffix(resource)
    def __resources_handler__():
        kwargs = {param: request.args.get(param) for param in params}
        return AstrAPI.handle_resource(resource, kwargs)


# Not Found --
if True:
    @api_route('<path:p>', methods = ['POST', 'PUT', 'GET', 'PATCH', 'DELETE'])
    def notfound(p):
        return jsonify({'error': 404, 'msg': 'api route ' + p + ' not found'})

@app.route('/<path:p>')
def index(p):
    return jsonify({'error': 404, 'msg': 'route ' + p + ' not found'})

def run():
    return app.wsgi_app
    #return app.run()
