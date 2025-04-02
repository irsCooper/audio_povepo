FROM python:3.12-slim

RUN mkdir audio_povepo
WORKDIR /audio_povepo

COPY ./requirements.txt /audio_povepo

RUN pip3 install -r requirements.txt
    
COPY . .

CMD ["sh", "-c", "sleep 5; alembic upgrade head && python3 main.py"]