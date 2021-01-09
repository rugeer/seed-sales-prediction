# Seed sales prediction algorithm and web service

Predict sales of flower seeds for one year (12 months)

## Setup

### Installation


- Install the package from source as following

```bash
pip install seed-sales-prediction-1.0.tar.gz
```

- Or directly from git:

```bash
pip install git+https://github.com/rugeer/seed-sales-prediction.git
```


### Start the web-service

- Start the server. By default host is 127.0.0.1 and port is 5000. You can change this, see the 
  [Command-line options](#Command-line options) section

```bash
start-seed-sales-predictor-server 
```

- Then visit [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs) to see the interactive API docs 

### Command-line options

```bash
Usage: start-seed-sales-predictor-server [OPTIONS]

  Start sales prediction server.

Options:
  --help          Show this message and exit.
  --host TEXT     Host
  --port INTEGER  Port
```

## Interactive API docs

- Once you start the webserver just visit `http://127.0.0.1:5000/docs` for the default settings. 
- This will load up interactive API documentation based on SwaggerAPI
- If you specify custom host/port then just visit `http://<your_specified_host>:<your_specified_port>/docs`
- The interactive website allows you to test the API's and see the schemas.

## Theory

- The model is based on Bayesian statistics for modeling the mean value of monthly sales using Normal conjugate priors.
- The model parameters get updated with arrival of new monthly sales data for each month, and the model becomes more precise. 
- The paper for calculating the posterior can be found [here](https://people.eecs.berkeley.edu/~jordan/courses/260-spring10/lectures/lecture5.pdf)
- The modelling of yearly sales is based on the property of normal distributions where the summations of normals is also a normal
- The 95% predictive interval is based on the yearly sales normal distribution. 
- Currently, I set a fixed value for standard deviation of the monthly sales
  (the EXPECTED_MONTHLY_SALES_VARIANCE variable in settings.py), which is not very precise (just a best guess), 
  so in the next iteration, this variable should be random as well (also in the paper).
