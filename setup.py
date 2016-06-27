import os
from distutils.core import setup

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="eventkit",
    version="0.2",
    author="",
    author_email="",
    description="eventkit, based on GeoNode",
    long_description=(read('readme.md')),
    # Full list of classifiers can be found at:
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - Planning',
    ],
    license="BSD",
    keywords="eventkit geonode django",
    url='https://github.com/eventkit/eventkit',
    packages=['eventkit',],
    include_package_data=True,
    zip_safe=False,
)
