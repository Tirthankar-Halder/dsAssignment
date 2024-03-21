FROM mysql:8.0-debian

COPY deploy.sh /always-initdb.d/


RUN apt-get update -y && \
	apt-get install -y python3-pip python3-dev
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
# RUN pip3 install -r requirements.txt 
RUN pip3 install -r requirements.txt --break-system-packages


RUN apt-get update
RUN apt-get -y install ca-certificates curl
RUN apt-get -y install sudo iputils-ping
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
RUN chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update
RUN apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
RUN apt-get -y install docker-ce-cli 

COPY . /app
RUN chmod +x /app/custom-entry.sh



###Installation of dokcker file
# RUN apt-get update
# RUN apt-get -y install sudo iputils-ping
# RUN apt-get -y install ca-certificates curl gnupg
# RUN install -m 0755 -d /etc/apt/keyrings
# RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
# RUN chmod a+r /etc/apt/keyrings/docker.gpg
# RUN echo \
#   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
#   $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
#   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# # RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
# RUN apt-get update
# # RUN apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# RUN apt-get -y install docker-ce-cli 




ENV USER=theuser
RUN adduser --home /home/$USER --disabled-password --gecos GECOS $USER \
  && echo "$USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER \
  && chmod 0440 /etc/sudoers.d/$USER \
  && usermod -aG docker $USER \
  && chsh -s /bin/zsh $USER
USER $USER

ENV HOME=/home/$USER
# RUN chmod 777 /var/run/docker.sock
ENV MYSQL_ROOT_PASSWORD="password"



# COPY . /app
# CMD ["python3","./loadbalancer.py"]

EXPOSE 5000

ENTRYPOINT ["/app/custom-entry.sh"]
CMD ["mysqld"]






















#Modified 
# # Set timezone:
# ENV DEBIAN_FRONTEND=noninteractive
# RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone
# RUN apt install -y tzdata libterm-readline-gnu-perl
# RUN dpkg-reconfigure -f noninteractive tzdata
# RUN apt -y install mysql-server
# # RUN apt-get -y install systemd
# # RUN systemctl restart mysql.service
# RUN mysql -u root -p mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';"
