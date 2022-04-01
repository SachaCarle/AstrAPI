# AstrAPI
Astrological API

# lib development
as production development
~~~
> python setup.py develop
> waitress-serve --call 'astrapi:run'
~~~
or in ./astrapi/
~~~
> flask run
~~~

# production
~~~
> python setup.py bdist_wheel
> pip3 install dist/AstrAPI-1.0.1-py3-none-any.whl
> waitress-serve --call 'astrapi:run'
~~~

# pip : libraries
behave
requests
flatlib
wheel
waitress