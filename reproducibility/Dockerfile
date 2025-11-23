FROM python:3.10-bookworm

COPY pyproject.toml .

COPY src src

RUN mkdir -p /reproducibility
RUN mkdir -p /reproducibility/results

RUN pip install -e .

CMD [ "python", "./src/main.py" ]