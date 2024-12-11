FROM tiangolo/uvicorn-gunicorn:latest

WORKDIR /fastapi


COPY ./fastapi/requirements.txt .

RUN pip install -r requirements.txt

COPY ./fastapi/ .

COPY ./mongo/basededatos.py .

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]