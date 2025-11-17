FROM python:3.10-bookworm

COPY reproducibility/requirements.txt .

COPY src .

RUN mkdir -p /results

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./src/main.py" ]