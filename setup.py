from setuptools import setup

setup(
    name="djes",
    version="1.0",
    description="Indexing Django models for Elasticsearch.",
    author="Masha Sabo",
    url="https://github.com/maria-sabo/djes",
    packages=['django_es', 'django_es_f', 'dj_es'],
)