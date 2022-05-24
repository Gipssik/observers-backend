FROM python:3.10

WORKDIR /code/backend

COPY requirements.txt /code/backend/
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /code/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]