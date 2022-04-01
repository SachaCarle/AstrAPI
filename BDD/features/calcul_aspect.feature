Feature: test aspect calcul endpoint

Scenario: setup request and result
    Given the endpoint calcul_aspect.
        and planet_a as a json param.
        and planet_b as a json param.
        and degree_a as a json param.
        and degree_b as a json param.
        and sign_a as a json param.
        and sign_b as a json param.
        and mercury is the planet_a.
        and neptune is the planet_b.
        and 26.392245886486215 is the degree_a.
        and 27.60606298048259 is the degree_b.
        and aries is the sign_a.
        and capricorn is the sign_b.
    Then post json to the endpoint.
        and assert the status code is 200.

Scenario: assert result format
    Then assert the result contains "type" key.
    Then assert the result contains "accuracy" key.
    Then assert the result contains "planet_a" key.
    Then assert the result contains "planet_b" key.
