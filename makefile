BASE_IMAGE=httprunnermanager
BASE_VERSION=v1.0.0

MYSQL_NAME=my-mysql
MYSQL_PASSWORD=mysql123456

all: build run-mysql prepare run

build:
	cp HttpRunnerManager/settings.py HttpRunnerManager/settings.py.bak
	sed "s|'PASSWORD'.*|'PASSWORD': '${MYSQL_PASSWORD}',|g" HttpRunnerManager/settings.py.bak |\
		sed "s|'HOST'.*|'HOST': 'mysql',|g" > HttpRunnerManager/settings.py

	docker build -t ${BASE_IMAGE}:${BASE_VERSION} .


prepare:
	docker run -it --rm  --link ${MYSQL_NAME}:mysql     \
		${BASE_IMAGE}:${BASE_VERSION}        sh -c      \
		'python manage.py makemigrations ApiManager &&   \
		python manage.py migrate                   &&   \
		python manage.py createsuperuser'


run-mysql:
	docker run --name ${MYSQL_NAME} -p 3306:3306 -e MYSQL_ROOT_PASSWORD=${MYSQL_PASSWORD} -d mysql:5.7
	# wait mysql server start
	sleep 10
	docker exec -it ${MYSQL_NAME} mysql -uroot -p${MYSQL_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS HttpRunner default charset utf8 COLLATE utf8_general_ci;"

run:
	docker run -id -d -p 8000:8000 --link ${MYSQL_NAME}:mysql  ${BASE_IMAGE}:${BASE_VERSION}

.PYONY: all build
