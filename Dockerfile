# syntax=docker/dockerfile:1
FROM python:latest
WORKDIR /app
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip
RUN pip3 install --upgrade -r requirements.txt
RUN pip3 uninstall discord.py -y
COPY . .
CMD [ "python3", "main.py" ]