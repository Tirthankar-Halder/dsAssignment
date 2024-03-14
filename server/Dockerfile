FROM ubuntu:20.04
RUN apt-get update -y && \
	apt-get install -y python3-pip python3-dev
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

# RUN apk add --no-csache su-exec
# RUN set -ex && apk --no-cache add sudo
# ENV PYTHONUNBUFFERED=1
# RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
# RUN apk add --update --no-cache py3-pip
# RUN python3 -m pip install --break-system-packages --no-cache-dir -r requirements.txt
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN pip install -r requirements.txt --break-system-packages
COPY . /app
EXPOSE 5000
# Set environment variable for server ID
ENV SERVER_ID="example_value"

CMD ["python3","./server.py"]
