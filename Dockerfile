FROM septimusd/ffrbot:3.6.7-alpine

WORKDIR /usr/src/app
COPY main.py .
COPY token.txt .

CMD ["python", "./main.py"]

