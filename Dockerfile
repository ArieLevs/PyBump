FROM python:3.13-slim

LABEL maintainer="Arie Lev <levinsonarie@gmail.com>" \
      description="Python version bumper"

WORKDIR /package

COPY src src
COPY pyproject.toml .
COPY LICENSE .
COPY README.rst .
COPY requirements.txt .
RUN pip install .

# clean package files
RUN rm -rf /package

RUN useradd -m pybump

USER pybump
WORKDIR /home/pybump

# execute simle version test
RUN pybump --version
ENTRYPOINT ["pybump"]