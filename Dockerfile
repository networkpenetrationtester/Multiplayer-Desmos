FROM python:latest

# I NEED to figure out how to transfer this venv into docker, so every time I make a small change it doesn't re-download like 3 gb of packages

COPY requirements.txt .
COPY ./src .

RUN pip install -r requirements.txt
