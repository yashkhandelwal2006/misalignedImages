# Correcting misaligned Document Images

## Setup

To set up the application, you need Python 3.7. After cloning the repository change to the project directory and install the dependencies via:

```
pip install -r requirements.txt

```

## Usage

To start the app , execute

```
python api.py

```

The application will then be available at `localhost:9000`. You can test the api using `curl`, e.g. via

```
curl http://localhost:9000/

```

The commands should output StatusCode : 200

Run the following commands to create input and output directories

```
mkdir inputs
mkdir outputs

```

For testing on images run the following python script which reads files from "inputs" directory and saves the aligned images to "outputs" directory.

```
python test.py

```