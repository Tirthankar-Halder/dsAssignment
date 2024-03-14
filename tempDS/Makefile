all:
	sudo docker-compose build
	cd ./server/ && sudo docker build -t server .
	sudo docker-compose up 

build:
	sudo docker-compose build
	cd ./server/ && sudo docker build -t server .

up:
	sudo docker-compose up -d

down:
	sudo docker ps -aq | xargs sudo docker stop | xargs sudo docker rm
	sudo docker-compose down
	
