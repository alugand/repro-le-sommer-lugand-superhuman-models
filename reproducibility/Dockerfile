FROM python:3.10-bookworm

COPY requirements.txt .

COPY ../src .

RUN mkdir -p /results/negated_pairs
RUN mkdir -p /results/bayes

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./src/main.py" ]