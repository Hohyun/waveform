FROM python:2

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update
RUN apt install -y build-essential libssl-dev zlib1g-dev
RUN apt install -y libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev
RUN apt install -y xz-utils 
RUN apt install -y ffmpeg

COPY . .

CMD [ "python", "./waveform.py" ]
