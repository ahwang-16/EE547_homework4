FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY schema.sql load_data.py queries.py ./

CMD ["python", "load_data.py"]
