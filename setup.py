from setuptools import setup

setup(
    name='AstrAPI',
    version='1.0.1',
    long_description=__doc__,
    packages=['astrapi'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'behave', 'requests', 'flatlib', 'wheel', 'waitress']
)