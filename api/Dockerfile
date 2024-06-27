FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader stopwords

COPY api/ api/
COPY shared/ shared/

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["python", "api/app.py"]