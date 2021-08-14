FROM python:3.9-slim

LABEL maintainer="Arie Lev <levinsonarie@gmail.com>" \
      description="Python version bumper"

WORKDIR package

COPY src src
COPY setup.py .
COPY LICENSE .
COPY README.rst .
RUN python ./setup.py install

WORKDIR /

# clean package files
RUN rm -rf /package

# execute simle version test
RUN pybump --version
ENTRYPOINT ["pybump"]