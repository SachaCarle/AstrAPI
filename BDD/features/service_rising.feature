Feature: test interpretation resources endpoints

    Scenario: test a empty resource
        Given the resource endpoint rising_sign.
            and sign as a query param.
            and $random_sign is the sign.
        Then get the resource endpoint.
            and assert the status code is 200.
            and assert the result is empty.

    Scenario: test a 1 element resource
        Then post "xyz" to the resource endpoint.
            and assert the status code is 200.
        Then get the resource endpoint.
            and assert the status code is 200.
            and assert the result is not empty.
            and assert the result contains 1 entries.
            and assert the result contains "xyz".

    Scenario: test a multiple element resource
        Then post "abc" to the resource endpoint.
            and assert the status code is 200.
        Then get the resource endpoint.
            and assert the status code is 200.
            and assert the result is not empty.
            and assert the result contains 2 entries.
            and assert the result contains "xyz".
            and assert the result contains "abc".

    Scenario: Delete a element resource
        Then delete "xyz" from the resource endpoint.
            and assert the status code is 200.
            and assert the result is not empty.
            and assert the result contains 1 entries.
        Then delete "abc" from the resource endpoint.
            and assert the status code is 200.
            and assert the result is empty.
