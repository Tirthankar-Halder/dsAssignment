FROM ubuntu:20.04
RUN apt-get update -y && \
	apt-get install -y python3-pip python3-dev
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
#from Assignment docs
# RUN apt-get update
# RUN apt-get -y install sudo
# RUN apt-get -y install apt-transport-https ca-certificates curl gnupg software-properties-common
# RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
# RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
# RUN apt-get update
# RUN apt-get -y install docker-ce-cli

# ENV USER=theuser
# RUN adduser --home /home/$USER --disabled-password --gecos GECOS $USER \
#   && echo "$USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER \
#   && chmod 0440 /etc/sudoers.d/$USER \
#   && groupadd docker \
#   && usermod -aG docker $USER \
#   && chsh -s /bin/zsh $USER
# USER $USER

# ENV HOME=/home/$USER

#Modified my me
RUN apt-get update
RUN apt-get -y install sudo iputils-ping
RUN apt-get -y install ca-certificates curl gnupg
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN chmod a+r /etc/apt/keyrings/docker.gpg
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
RUN apt-get update
# RUN apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
RUN apt-get -y install docker-ce-cli 



ENV USER=theuser
RUN adduser --home /home/$USER --disabled-password --gecos GECOS $USER \
  && echo "$USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER \
  && chmod 0440 /etc/sudoers.d/$USER \
  && groupadd docker \
  && usermod -aG docker $USER \
  && chsh -s /bin/zsh $USER
USER $USER

ENV HOME=/home/$USER
# RUN chmod 777 /var/run/docker.sock


COPY . /app
CMD ["python3","./loadbalancer.py"]
EXPOSE 5000
