Feature: test placement calcul endpoint

Scenario: setup request and result
    Given the endpoint chart_aspects.
        and lon as a json param.
        and lat as a json param.
        and day as a json param.
        and month as a json param.
        and year as a json param.
        and hour as a json param.
        and minute as a json param.
        and utcoffset as a json param.
        and -4.487056 is the lon.
        and 48.377107 is the lat.
        and 6 is the day.
        and 4 is the month.
        and 1996 is the year.
        and 10 is the hour.
        and 4 is the minute.
        and 2 is the utcoffset.
    Then post json to the endpoint.
        and assert the status code is 200.

Scenario: assert result format
    Then assert the result contains "opposition" key.
    Then assert the result contains "square" key.
    Then assert the result contains "cunjunction" key.
    Then assert the result contains "trine" key.
    Then assert the result contains "sextile" key.
    Then assert the result contains "quincunx" key.
