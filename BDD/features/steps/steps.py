import logging, time
from behave import given, when, then, step
from astrapi_request import AstrAPIWrapper
from random import choice

RESSOURCE_TABLE_NAME = [
    'planet_sign_txts', 'housecusp_sign_txts', 'ascendant_sign_txts',
    'midheaven_sign_txts', 'planet_house_txts', 'ruler_house_txts',
    'various_txts'
]

planets = [
    'pluto', 'sun', 'moon', 'mercury', 'venus', 'jupiter',
    'mars', 'uranus', 'saturn', 'neptune'
]
signs = [
    'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra',
    'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'
]
houses = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
]
aspects = 'square', 'opposition', 'cunjunction', 'trine', 'sextile', 'quincunx'

fun = {
    'random_planet': lambda: choice(planets),
    'random_sign': lambda: choice(signs),
    'random_house': lambda: choice(houses),
}

result = None
def result_data():
    assert not result is None, str(type(result))
    if isinstance(result, dict):
        if 'data' in result:
            return result['data']
        return result
    else:
        raise Exception("Request failed, result = " + str(result))

api = AstrAPIWrapper('http://127.0.0.1:5000/api/v1/')

# --- Helper --- #


# --- Steps --- #

@given('the resource endpoint {endpoint:w}.')
def step_impl(ctx, endpoint):
    time.sleep(30)
    api.setCurrentEndpoint(endpoint, clean=True, resource=True)

@given('the endpoint {endpoint:w}.')
def step_impl(ctx, endpoint):
    time.sleep(30)
    api.setCurrentEndpoint(endpoint, clean=True)

@given('{param} as a {type} param.')
def step_impl(ctx, param, type):
    if type == "query":
        api.addParam(param)
    elif type == "json":
        api.addBodyParam(param)
    else:
        raise NotImplementedError(u'STEP: Given ' + param + ' as a ' + type + '.')

@given('{value} is the {param}.')
def step_impl(ctx, value, param):
    if value[0] == "$":
        value = fun[value[1:]]()
    api.setParam(param, value)

@then('assert the status code is {code:d}.')
def step_impl(ctx, code):
    assert api.r.status_code == code, code

@then('assert the result is empty.')
def step_impl(ctx):
    rd = result_data()
    assert not (rd is None), rd
    assert len(rd) == 0, rd

@then('assert the result is not empty.')
def step_impl(context):
    rd = result_data()
    assert not rd is None
    assert len(rd) > 0, "result at " + api.endpoint + " is empty." + str(result)

@then('assert the result contains "{value:w}".')
def step_impl(context, value):
    rd = result_data()
    assert not rd is None
    assert len(rd) > 0, "result at " + api.endpoint + " is empty."
    assert value in rd, "result at " + api.endpoint + " do not contain: " + value + '.'\
        + '\n\t' + str(rd)

@then('assert the result contains {value:d} entries.')
def step_impl(context, value):
    rd = result_data()
    assert not rd is None
    assert len(rd) == value, "result at " + api.endpoint + " is not " + str(value) + " long." + '\n\t' + str(rd)

@then('assert the result contains "{value:w}" key.')
def step_impl(context, value):
    rd = result_data()
    assert value in rd, 'Key ' + value + ' not present in result.' + str(rd)


@then ('post "{value:w}" to the {mod:w} endpoint.')
def step_impl(context, value, mod):
    global result
    result = api.post(value)

@then ('post {mod:w} to the endpoint.')
def step_impl(context, mod):
    time.sleep(5)
    global result
    assert mod == 'json'
    result = api.post(None)

@then ('delete "{value:w}" from the {mod:w} endpoint.')
def step_impl(context, value, mod):
    time.sleep(5)
    global result
    result = api.delete(value)

@then ('get the {mod:w} endpoint.')
def step_impl(context, mod):
    time.sleep(2)
    global result
    result = api.get()