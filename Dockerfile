FROM python:3.10.12
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y gettext

RUN pip install --upgrade pip


WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD [ "sh", "-c", "python3 create_tables.py && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" ] 