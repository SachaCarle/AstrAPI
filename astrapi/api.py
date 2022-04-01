from flask import jsonify, request, Response
from astrapi import DBInterface
from .astro_report import points, aspects, houses, signs, master_schema, minor_schemas, calculate_chart, calculate_chart_placements, calculate_chart_houses, calculate_chart_aspects, calculate_aspect, report_json_to_html, report_head
from .utils import dikwarg, dict_flatten_values
import sys, json, traceback

dbi = DBInterface()

#debug or feature
import pprint
pp = pprint.PrettyPrinter(indent=4)
#--

# api block
def get_json():
    try:
        data = request.json
        if data is None:
            data = json.loads(request.data)
    except Exception as e:
        raise Exception('Unable to get json body: ' + str(e) + "\ndata:\t" + str(request.data))
    return data
def dispatch(*keys):
    data = get_json()
    res = []
    for k in keys:
        try:
            item = data[k]
        except Exception:
            raise Exception(k)
        res.append(item)
    return res
def json_return(this):
    if isinstance(this, (list, tuple, set)):
        return jsonify({'data': this})
    return jsonify(this)


class AstrAPI:
    RESOURCES = {
      # 'resource' : ['query', 'parameter']
        'planet_sign' : ['planet', 'sign'],
        'planet_house' : ['planet', 'house'],
        'ruler_house' : ['ruler', 'house'],
        'house_sign' : ['house', 'sign'],
        'midheaven_sign' : ['sign'],
        'rising_sign' : ['sign'],
        'various' : ['key']
    }
    @staticmethod
    def onFail(ex):
        traceback.print_exc(file=sys.stderr)
        return json_return({
                'error': 'Error with parameter: ' + str(ex)
            })
    @staticmethod
    def handle_resource(resource, kwargs, method=None):
        debug = True if method is None else False
        method = request.method if method is None else method
        if method  == 'DELETE':
            data = request.data.decode('utf-8')
            x = dbi.delete(resource + '_txts', data, **kwargs)
        if method == 'POST':
            data = request.data.decode('utf-8')
            x = dbi.set(resource + '_txts', data, **kwargs)
        else:
            x = dbi.get(resource + '_txts', **kwargs)
        if debug:
            print ("HANDLE RESROUCE RESULT: ", x)
        return x
    @staticmethod
    def handle(path):
        try:
            if path in ['chart_placements', 'chart_houses', 'chart_aspects', 'natal_report', 'natal_report_html']:
                chart = calculate_chart(*dispatch("year", "month", "day", "hour", "minute", "utcoffset", "lat", "lon"))
                if path in ['chart_placements', 'chart_aspects', 'natal_report', 'natal_report_html']:
                    pls = calculate_chart_placements(chart)
                    result = pls
                if path in ['chart_houses', 'natal_report', 'natal_report_html']:
                    hs = calculate_chart_houses(chart)
                    result = hs
                if path in ['chart_aspects', 'natal_report', 'natal_report_html']:
                    asps = calculate_chart_aspects(chart)
                    result = asps
                if path in ['natal_report', 'natal_report_html']:
                    planets_report, houses_report = AstrAPI.writeReport(chart, pls, hs, asps)
                    report_json = {
                        'planets': planets_report,
                        'houses': houses_report
                    }
                    result = report_json
                if path in ['natal_report_html']:
                    html_content = AstrAPI.formatReport(chart, report_json)
                    return "<body><p>" + html_content + "</p></body>" # html return
            elif path == 'calcul_aspect':
                asp = calculate_aspect(*dispatch("planet_a", "planet_b", "degree_a", "degree_b", "sign_a", "sign_b"))
                result = asp
            else:
                assert path in AstrAPI.RESOURCES.keys()
                kwargs = {param: request.args.get(param) for param in AstrAPI.RESOURCES[path]}
                result = AstrAPI.handle_resource(path, kwargs)
        except Exception as e:
            return AstrAPI.onFail(e)
        return json_return(result)
    @classmethod
    def writeReport(kls, chart, pls, hs, asps):
        with dbi: # allow only reading, not put or delete
            dbi.loads('planet_sign_txts', 'planet_house_txts', 'house_sign_txts', 'ruler_house_txts', 'rising_sign_txts', 'midheaven_sign_txts')
            rps, hps = {}, {}
            asps = dict_flatten_values(asps)
            for p, placement in pls.items():
                asplist = []
                for a in asps:
                    if p == a['planet_a'] or p == a['planet_b']:
                        asplist.append(a)
                if p in ['midheaven', 'rising']:
                    rps[p] = {
                                'placement': placement,
                                'aspects': asplist,
                    #            'intro': 'add from various_txts if exist',
                                'sign_txt': kls.handle_resource(p + '_sign', dikwarg(sign=placement['sign'].lower()), method='GET'),
                                #'house_txt': kls.handle_resource('planet_house', dikwarg(planet=p, house=placement['house']), method='GET'),
                            }
                    continue
                rps[p] = {
                    'placement': placement,
                    'aspects': asplist,
    #                'intro': 'add from various_txts if exist',
                    'sign_txt': kls.handle_resource('planet_sign', dikwarg(planet=p, sign=placement['sign'].lower()), method='GET'),
                    'house_txt': kls.handle_resource('planet_house', dikwarg(planet=p, house=placement['house']), method='GET'),
                }
            for h, house in hs.items():
                ruler_house = None
                for k,p in pls.items():
                    if k == house['ruler']:
                        ruler_house = p['house']
                assert not ruler_house is None, (h, p['name'], house['ruler'], p['house'])
                hps[h] = {
                    'house': h,
                    'sign': house['sign'],
                    'ruler': house['ruler'],
    #                'intro': 'add from various_txts if exist',
                    'cusp_txt': kls.handle_resource('house_sign', dikwarg(house=h, sign=house['sign'].lower()), method='GET'),
                    # GET RULER_HOUSE PLACEMENT FROM (1 + signs.index(house['sign'].lower()))
                    'ruler_txt': kls.handle_resource('ruler_house', dikwarg(ruler=ruler_house, house=house['house']), method='GET'),
                }
        return rps, hps
    @classmethod
    def formatReport(kls, chart, report_json):
        return '<html>' + report_head() + report_json_to_html(chart, report_json) + '</html>'


