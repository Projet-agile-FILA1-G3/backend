FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader stopwords

COPY crawler/ crawler/
COPY shared/ shared/

EXPOSE 5000

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["python", "crawler/app.py"]