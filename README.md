# DD2480-CI
## Setup

Install Python 3.13.1

1. When you have installed python, Use the following command to create a virtual environment:

```bash
python3 -m venv venv
```

2. To enter virtual environment

    To enter virtual environment (For MacOS), run:

    ```bash
    source venv/bin/activate
    ```

    To enter virtual environment (For Windows), run:

    ```bash
    ./venv/bin/activate
    ```

    - Use command ```deactivate``` to close environment

## Running the program

1. To run server, use following command:

```bash
python src/app/CIServer.py
```

2. To run tests run the following command:
```bash
pytest src/test/CIServer_test.py
```



