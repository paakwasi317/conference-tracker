# Conference-tracker
This project is designed to take a list of conference talks and their duration as a csv file and returns a schedule(tracks)

## How to run project

To build and run the project, follow these steps:
1. Run `make all` to install dependencies, run tests, and bring up Docker containers.
2. Open your browser and type [http://0.0.0.0:8000/tracker](http://0.0.0.0:8000/tracker)
3. Upload your csv file. eg: [sample csv](https://drive.google.com/file/d/1-5Af6_HEL3e4aOpvEcxVeLJk61utTmHl/view)

## How to stop project
1. To stop the Docker containers and perform cleanup, run `make down`.

## Dependencies

- fastapi
- pydantic
- uvicorn
- python-multipart
- fastapi-pagination
- jinja2
- sqlalchemy-json
- pandas
- loguru

## Targets
`Make` command can be run in combination of any of these targets

### `all`

The `all` target is a combination of the `install`, `test`, and `up` targets. It ensures that the project dependencies is properly installed, tests are executed, and the Docker containers are brought up.

### `clean`

The `clean` target is responsible for cleaning up the project directory by removing temporary and generated files. This includes removing `.pyc` files, `__pycache__` directories, temporary files, and build artifacts.

### `test`

The `test` target runs unit and integration tests for the project. It uses the `unittest` module to execute the tests defined in `tests/unit/test_scheduler.py` and `tests/integration/test_upload_file.py`.

### `install`

The `install` target sets up a virtual environment (`venv` directory) for the project. It checks if the virtual environment already exists and creates it if not. It then activates the virtual environment and installs project dependencies from the `requirements.txt` file using `pip`.

### `up`

The `up` target uses `docker-compose` to build and bring up the Docker containers defined in the project. It ensures that the application environment is set up and running.

### `down`

The `down` target uses `docker-compose` to stop and remove the Docker containers. It also invokes the `clean` target to perform additional cleanup.
