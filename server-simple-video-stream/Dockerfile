FROM docker.io/mangelajo/jetson-tx2-dlib:latest 
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC \
    ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    apt-get update && \
    apt-get install -y python3-markupsafe nvidia-opencv python3-opencv\
                       python3-requests
RUN pip3 install flask
WORKDIR /app

COPY *.py /app
ADD static/ /app/static/
ADD templates/ /app/templates/
RUN mkdir /app/faces
COPY faces /app/faces
ENV FLASK_APP=server
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
CMD python3 -m flask run --host 0.0.0.0
