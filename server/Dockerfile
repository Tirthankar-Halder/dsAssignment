# FROM ubuntu:20.04
FROM mysql:8.0-debian


COPY deploy.sh /always-initdb.d/
# RUN apt-get update -y && \
# 	apt-get install -y python3-pip python3-dev
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip


WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
# RUN pip install --upgrade pip
RUN pip install -r requirements.txt --break-system-packages
COPY . /app
RUN chmod +x /app/custom-entry.sh



# ENV USER=theuser
# RUN adduser --home /home/$USER --disabled-password --gecos GECOS $USER \
#   && chsh -s /bin/zsh $USER
# RUN touch /app/shardDB.db
# RUN chown $USER /app/shardDB.db

# Set environment variable for server ID
ENV SERVER_ID=""

# USER $USER
# ENV HOME=/home/$USER
ENV MYSQL_ROOT_PASSWORD="password"

# EXPOSE 5000
ENTRYPOINT ["/app/custom-entry.sh"]
CMD ["mysqld"]
# CMD ["python3","./server.py"]


# FROM ubuntu:20.04
# FROM mysql:8.0-debian

# COPY deploy.sh /always-initdb.d/
# COPY ./requirements.txt /srvr/requirements.txt
# COPY . /srvr
# WORKDIR /srvr

# RUN apt-get update -y && \
# 	apt-get install -y python3-pip python3-dev

# RUN pip install -r requirements.txt

# ENV USER=theuser
# RUN adduser --home /home/$USER --disabled-password --gecos GECOS $USER \
#   && chsh -s /bin/zsh $USER
# RUN touch /srvr/shard.db
# RUN chown $USER /srvr/shard.db

# # Set environment variable for server ID
# ENV SERVER_ID=""

# USER $USER
# ENV HOME=/home/$USER
# ENV MYSQL_ROOT_PASSWORD="abc"

# CMD ["python3","./server.py"]
