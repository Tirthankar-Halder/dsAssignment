FROM mysql:8.0-debian


COPY deploy.sh /always-initdb.d/
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip


WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt --break-system-packages
COPY . /app
RUN chmod +x /app/custom-entry.sh

ENV SERVER_ID=""

ENV USER=theuser
RUN adduser --home /home/$USER --disabled-password --gecos GECOS $USER \
  && chsh -s /bin/zsh $USER
RUN chown -R $USER /app

USER $USER
ENV HOME=/home/$USER
ENV MYSQL_ROOT_PASSWORD="password"
# EXPOSE 5000
ENTRYPOINT ["/app/custom-entry.sh"]
CMD ["mysqld"]
