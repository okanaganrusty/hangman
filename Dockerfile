FROM python:3

COPY app /app
WORKDIR /app

CMD ["python3", "hangman.py"]
