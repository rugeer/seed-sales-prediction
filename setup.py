from setuptools import setup

packages = [
    "click==7.1.2",
    "uvicorn==0.13.3",
    "fastapi==0.63.0",
    "pandas==1.2.0"
]

setup(name='Seed Sales Prediction Webservice',
      version='1.0',
      author='Robin',
      description='Web service for predicting seed sales for a year',
      packages=['seed_sales_prediction'],
      entry_points={
          'console_scripts': [
              'start-seed-sales-predictor-server=seed_sales_prediction.cli.main:app'
          ]
      },
      install_requires=packages,
      python_requires='>=3.6')

