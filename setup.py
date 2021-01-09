from setuptools import setup, find_packages

packages = [
    "click==7.1.2",
    "uvicorn==0.13.3",
    "fastapi==0.63.0",
    "pandas==1.2.0",
    "pydantic==1.7.3"
]

setup(name='Seed Sales Prediction Webservice',
      version='1.0',
      author='Robin',
      description='Web service for predicting seed sales for a year',
      packages=find_packages('.', exclude=['tests', 'tests.*']),
      entry_points={
          'console_scripts': [
              'start-seed-sales-predictor-server=seed_sales_prediction.cli.main:app'
          ]
      },
      install_requires=packages,
      python_requires='>=3.6')

