FROM ubuntu:20.04
RUN apt-get update -y && \
	apt-get install -y python3-pip python3-dev
WORKDIR /app
COPY ./requrirements.txt /app/requrirements.txt
RUN pip install -r requrirements.txt
COPY . /app
# Set environment variable for server ID
ENV SERVER_ID=""

CMD ["python3","./server.py"]
