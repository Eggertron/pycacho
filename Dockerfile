FROM python:latest

WORKDIR /tmp

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt
    

WORKDIR /app

EXPOSE 5000

CMD ["python", "backend.py"]
