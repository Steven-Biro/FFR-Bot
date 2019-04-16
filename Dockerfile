FROM gorialis/discord.py:3.7.3-alpine-pypi-minimal

WORKDIR /usr/src/app
COPY main.py .
COPY token.txt .

CMD ["python", "./main.py"]

