from setuptools import setup

setup(name='sky-scraper', version = '0.1', 
    description='For all of your cloud scraping needs',
    url='https://github.com/jdstregz/sky-scraper',
    author='Team 8 - CISC475',
    licence='MIT',
    packages=['sky-scraper'],
    install_requires=[
        'scrapy',
        'psycopg2',
        're',
        'scrapy_splash',
    ],
    zip_safe=False)