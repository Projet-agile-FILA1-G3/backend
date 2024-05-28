FROM python:3.11

WORKDIR /app

COPY requirements.txt .



RUN pip install --no-cache-dir -r requirements.txt

COPY api/ api/
COPY shared/ shared/

EXPOSE 5000

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["python", "api/app.py"]