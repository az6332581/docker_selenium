# docker_selenium
md selenium docker

cd docker_selenium
sudo docker compose build


xhost +local:root

sudo docker run -it \
  --name mood-scheduler-gui \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  docker_selenium