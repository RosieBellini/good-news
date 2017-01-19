FROM debian:jessie

ENV DOCKER_FIX: '                                        '

RUN apt-get -y update \
 && apt-get -y upgrade -y \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install \
        mysql-server \
        nginx-extras \
        curl \
        git \
        vim \
        python3 \
        python3-pip \
        python-setuptools


RUN easy_install pip


RUN pip3 install request
RUN pip3 install urllib5
#RUN pip3 install json
RUN pip3 install python-env
RUN pip3 install vaderSentiment

WORKDIR /app


COPY ["headline_analyser.py", "run.sh", ".env", "/app/"]


# Declare /data & /assets as a persistent volume
# (so they don't get removed when the server restarts)
VOLUME /data


# Declare the port we will use
EXPOSE 80


# Let our run script be run
RUN chmod +x /app/run.sh


# Start our application
CMD /app/run.sh