# FROM ubuntu:20.04
# # FROM mysql:8.0-debian
# # 

# # COPY deploy.sh /always-initdb.d/
# RUN apt-get update
# RUN apt-get install -y python3
# RUN apt-get install -y python3-pip


# WORKDIR /app
# COPY ./requirements.txt /app/requirements.txt
# RUN pip install -r requirements.txt --break-system-packages
# COPY . /app
# # RUN chmod +x /app/custom-entry.sh
# # ENV MYSQL_ROOT_PASSWORD="password"

# EXPOSE 5000
# # ENTRYPOINT ["/app/custom-entry.sh"]
# # CMD ["mysqld"]
# CMD ["python3","./shardManager.py"]


FROM ubuntu:20.04

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt 
COPY . /app
# WORKDIR /app

RUN apt-get update -y && \
	apt-get install -y python3-pip python3-dev

RUN pip3 install -r requirements.txt 

EXPOSE 5000
CMD ["python3","./shardmanager.py"]
