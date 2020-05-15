FROM python:3.7-slim
COPY . /app
WORKDIR /app
ENTRYPOINT python pybump/pybump.py
CMD echo TimorTheKing
