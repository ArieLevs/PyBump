FROM python:3-alpine

COPY . .

RUN python ./setup.py install

ENTRYPOINT ["pybump"]
