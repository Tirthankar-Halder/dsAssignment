all:
	sudo docker-compose build
	cd ./server/ && sudo docker build -t server .
	sudo docker-compose up 

build:
	sudo docker-compose build
	cd ./server/ && sudo docker build -t server .

loadbalancer:
	cd ./loadbalancer/ && sudo docker build -t loadbalancer .

up:
	sudo docker-compose up -d

restart:
	sudo docker ps -aq | xargs sudo docker stop | xargs sudo docker rm
	sudo docker-compose down
	sudo docker-compose build
	cd ./server/ && sudo docker build -t server .
	sudo docker-compose up

down:
	sudo docker ps -aq | xargs sudo docker stop | xargs sudo docker rm
	sudo docker-compose down
	# sudo docker system prune -a
	# sudo systemctl restart snap.docker.dockerd.service
	# @if [ "$$(sudo docker ps -aq)" ]; then \
    #     sudo docker rm -f $$(sudo docker ps -aq); \
	# fi
	# @if [ "$$(sudo docker images -aq)" ]; then \
	# 	sudo docker rmi -f $$(sudo docker images -aq); \
	# fi 
	
	
