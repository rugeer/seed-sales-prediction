# seed-sales-prediction
Predict sales of flower seeds for one year

## Setup

### Installation

- Install the package from source as following

```bash
pip install seed-sales-prediction-1.0.tar.gz
```

### Start the web-service

- Start the server. By default host is 127.0.0.1 and port is 5000. You can change this, use the `--help` command to find
the parameters.

```bash
start-seed-sales-predictor-server 
```

- Then visit `http://127.0.0.1:5000/docs` to see the interactive API docs 

- You can run to see the available parameters 

```bash 
start-seed-sales-predictor-server --help
```

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