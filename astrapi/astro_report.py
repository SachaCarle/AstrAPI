from flatlib.geopos import GeoPos
from flatlib.datetime import Datetime
from flatlib.chart import Chart
from flatlib.dignities import accidental, essential, tables
from flatlib.aspects import getAspect
from flatlib import const, props
#----------ASTROLOGY-LIBRARY-------------------------#

from .utils import schematize, organize, populate, Namespace, flatten

signs = [o.lower() for o in const.LIST_SIGNS]
points = flatten(((o.lower() for o in const.LIST_OBJECTS[:10]), ('rising', 'midheaven')))
aspects_degree = { 0:'cunjunction', 60: 'sextile', 90:'square', 120:'trine', 180:'opposition', 150:'quincunx' }
aspects = aspects_degree.values()
houses = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12

def getFlatKey(key):
    if key == 'rising':
        return 'House1'
    elif key == 'midheaven':
        return 'House10'
    elif isinstance(key, str):
        return key.capitalize()
    else:
        return "House" + str(key)

def getPoint(chart, key):
    fk = getFlatKey(key)
    if fk.startswith('House'):
        return chart.getHouse(fk)
    return chart.getObject(fk)

def orb_between(pa, pb):
    fa, fb = getFlatKey(pa), getFlatKey(pb)
    if fa.startswith('House'):
        orba = 2
    else:
        orba = props.object.orb[fa]
    if fb.startswith('House'):
        orbb = 2
    else:
        orbb = props.object.orb[fb]
    if orba > orbb:
        return orba
    else:
        return orbb

def ruler_of(sign):
    return tables.ESSENTIAL_DIGNITIES[sign]['ruler'].lower()


class Description(Namespace):
    def __repr__(self):
        if hasattr(self, 'description'):
            return self.description
        else:
            return self.__str__()
    def mold(self, obj, *args, **kwargs):
        if hasattr(self, 'key'):
            return getattr(obj, self.key)
        elif hasattr(self, 'get'):
            return getattr(obj, self.get)()
        elif hasattr(self, 'fun'):
            return self.fun(obj, *args, **kwargs)
        elif hasattr(self, 'kwarg'):
            return kwargs[self.kwarg]
        else:
            raise Exception('Molding error: no method for molding ' + str(self))
    def __call__(self, *args, **kwargs):
        res = self.mold(*args, **kwargs)
        if hasattr(self, 'type'):
            if self.type == 'string':
                assert isinstance(res, str), res
            elif self.type == 'object':
                assert isinstance(res, dict), res
            elif self.type == 'float':
                assert isinstance(res, float), res
            elif self.type == 'integer':
                assert isinstance(res, int), res
            elif self.type == 'bool':
                assert res in [True, False], res
        return res
def description_generator(description=None, **kwargs):
    def __descriptor__(key):
        if description is None:
            return Description(__name__=key, **kwargs)
        else:
            return Description(__name__=key, description=description, **kwargs)
    return __descriptor__

minor_schemas = {
    'placement': {
        'degree': description_generator('Position in astrological degree on the sign. beetween 0. and 30.', type="float", key="signlon"),
        'sign': description_generator('Name (in english) of astrological sign.', type="string", key="sign"),
        'house': description_generator('The house number where the object is. Beetween 1 and 12.', type="integer",
                                       fun = lambda obj, *args, chart=None, **kwargs: chart.houses.getObjectHouse(obj).num()),
        #'retro': description_generator('Is the object retrograde?', type="bool", get="isRetrograde"),
        'name': description_generator('The object name (in english). Can be a planet or Rising or Midheaven.', type="string", kwarg="name"),
    },
    'aspect': { # --desc-->
        'planet_a': description_generator('The first object contributing to the aspect. Can be a planet or Rising or Midheaven', type="string"),
        'planet_b': description_generator('The second object contributing to the aspect. Can be a planet or Rising or Midheaven', type="string"),
        'type': description_generator('The type of aspect the two planet make. Can be : square, opposition, cunjunction, trine, sextile, quincunx', type="string"),
        'accuracy': description_generator('The accuracy of the aspect beetween 0. and orb for that aspect.', type="float"),
    },
    'report_planet': {
        'placement': description_generator('The placement of the object.', type="object"),
        'aspects': description_generator('List of each aspect containing this object.', type="list"),
        'intro': description_generator('Static text describing the planet roles.', type="string"),
        'sign_txt': description_generator('Text interpretation according to sign.', type="string"),
        'house_txt': description_generator('Text interpretation according to house.', type="string"),
    },
    'report_house': {
        'house': description_generator('The house number.', type="integer"),
        'sign': description_generator('The sign (in english) where the house cusp is.', type="string"),
        'ruler': description_generator('The object ruling this house.', type="string"),
        'intro': description_generator('Static text describing the house influences.', type="string"),
        'cusp_txt': description_generator('Text interpreatation according to sign.', type="string"),
        'ruler_txt': description_generator('Text interpreatation according to ruler\'s house.', type="string"),
    }
    # exception pour rising et midheaven qui se feront sans doute patch
}

master_schema = {
    'placements': organize(schematize(minor_schemas['placement'], points)),
    'aspects': organize(schematize(minor_schemas['aspect'], aspects)),
    'report': {
        'planets': organize(schematize(minor_schemas['report_planet'], points)),
        'houses': organize(schematize(minor_schemas['report_house'], houses)),
        #'aspects': organize(schematize(minor_schemas['report_aspect'], aspects)),
    }
}

def calculate_chart(year, month, day, hour, minute, utcoffset, lat, lon):
    lat, lon = float(lat), float(lon)
    utcoffset = int(utcoffset)
    hdate = year + '/' + month + '/' + day
    time = hour + ':' + minute
    date = Datetime(hdate, time=time, utcoffset=utcoffset)
    pos = GeoPos(lat, lon)
    return Chart(date, pos, hsys=const.HOUSES_PLACIDUS,
                IDs=['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'])

import sys
def calculate_aspect(planet_a, planet_b, degree_a, degree_b, sign_a, sign_b):
    degree_a, degree_b = float(degree_a), float(degree_b)
    assert sign_a in signs and sign_b in signs
    assert degree_a < 30.0 and degree_a >= 0.0
    assert degree_b < 30.0 and degree_b >= 0.0
    assert planet_a in points and planet_b in points
    degree_a += (1 + signs.index(sign_a)) * 30.0
    degree_b += (1 + signs.index(sign_b)) * 30.0
    if degree_a > degree_b:
        delta = degree_a - degree_b
    else:
        delta = degree_b - degree_a
    orb = orb_between(planet_a, planet_b)
    for degree, name in aspects_degree.items():
        accuracy = delta
        if degree > 0:
            while accuracy > degree:
                #print ((degree, name, accuracy, delta), file=sys.stderr)
                accuracy = accuracy - degree
        if accuracy <= orb:
            return {
                'type': name,
                'planet_a': planet_a,
                'planet_b': planet_b,
                'accuracy': accuracy
            }
    return {
        'type': 'none',
        'planet_a': planet_a,
        'planet_b': planet_b,
        'accuracy': delta
    }

def calculate_chart_placements(chart):
    assert chart.isHouse10MC() and chart.isHouse1Asc(), "Error configuration flatlib: unexpected rising and midheaven."
    def _populate_method(key, value, chart):
        if key == 'rising':
            k = 'House1'
        elif key == 'midheaven':
            k = 'House10'
        elif isinstance(key, str):
            k = key.capitalize()
            return value.mold(chart.getObject(k), name=key, chart=chart)
        else:
            k = "House" + str(key)
        return value.mold(chart.getHouse(k), name=key, chart=chart)
    return populate(master_schema['placements'], _populate_method, chart)

def calculate_chart_aspects(chart):
    assert chart.isHouse10MC() and chart.isHouse1Asc(), "Error configuration flatlib: unexpected rising and midheaven."
    asps = { key:list() for key in aspects }
    for oi, pa in enumerate(points):
        for pb in points[oi+1:]:
            asp = getAspect(getPoint(chart, pa), getPoint(chart, pb), const.ALL_ASPECTS)
            if asp.type in aspects_degree.keys():
                asp_name = aspects_degree[asp.type]
                res = {
                    'type': asp_name,
                    'planet_a': pa,
                    'planet_b': pb,
                    'accuracy': asp.orb
                }
                asps[asp_name].append(res)
    return asps

def calculate_chart_houses(chart):
    chart_houses = []
    for house in houses:
        hn = str(house)
        ho = chart.getHouse('House' + hn)
        chart_houses.append(ho)
    return {
        house.num(): {
            'house': house.num(),
            'sign': house.sign,
            'degree': house.signlon,
            'ruler': ruler_of(house.sign)
        } for house in chart_houses
    }

#--------REPORT-GENERATOR-------------#

def human_degree(float_degree):
    ms = int(float_degree)
    ss = int((float_degree - float(ms)) * 60)
    return str(ms) + "°" + str(ss) + "'"

def html_sep():
    return '<br/>'

def _report_txts(txts):
    html = ""
    for txt in txts:
        html += '<p>' + str(txt) + '</p>' + html_sep()
    return html

def _report_aspects(planet, aspects):
    html = ""
    html += '<p>'
    for asp in aspects:
        html += planet.capitalize() + ' form a ' + asp['type'] + ' with '
        if asp['planet_a'] == planet:
            html += asp['planet_b']
        else:
            html += asp['planet_a']
        html += ' at ' + human_degree(asp['accuracy']) + ' accuracy.' + html_sep()
    html += '</p>'
    return html

def _report_planets(planets):
    html = "<h1>Planets interpretations:</h1>"
    for name, value in planets.items():
        html += '<div>'
        html += '<h2>' + name.capitalize() + ' in ' + value['placement']['sign'] + ' at degree ' + human_degree(value['placement']['degree']) + '</h2>'
        html += _report_txts(value['sign_txt'])
        html += _report_aspects(name, value['aspects'])
        if not name in ['rising', 'midheaven']:
            html += '<h3>' + name.capitalize() + ' in ' + str(value['placement']['house']) + ' House' + '</h3>'
            html += _report_txts(value['house_txt'])
        html += '</div>' + html_sep()
    return html

def _report_houses(houses):
    html = "<h1>Houses interpretations:</h1>"
    for name, value in houses.items():
        name = 'House ' + str(name)
        html += '<div>'
        html += '<h2>' + name + ' in ' + value['sign'] + '</h2>'
        html += _report_txts(value['cusp_txt'])
        html += '<h3>' + name + ' ruler is ' + value['ruler'].capitalize() + '</h3>'
        html += _report_txts(value['ruler_txt'])
        html += '</div>' + html_sep()
    return html

DEFAULT_CSS = """
body,
h1,
h3,
h4,
h5,
h6 {
    font-family: Arial, Helvetica, sans-serif;
    color: #D2D2F2;
}

p {
    line-height: 1.2em;
}

body {
    background: #0A0A2A;
    padding: 0 3% 0 3%;
}

div {
    text-align: center;
}

h2 {
    font-family: "Times New Roman", Times, serif;
    text-decoration: underline;
}

"""

def report_head(style=DEFAULT_CSS):
    return '<head><style>' + style + '</style></head>'

def report_json_to_html(chart, report):
    planets = _report_planets(report['planets'])
    houses = _report_houses(report['houses'])
    return '<body>' + planets + html_sep() + houses + '</body>'