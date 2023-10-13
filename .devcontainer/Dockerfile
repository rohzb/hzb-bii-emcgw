FROM mcr.microsoft.com/devcontainers/base:ubuntu as base

# Update packages
RUN apt-get update \
    && apt-get upgrade -y 
# and install few standard pacakged
RUN apt-get install -y \
        host \
        vim \
        mc

FROM base as python3.10
RUN apt-get install -y python3.10 python3-pip python3-venv

#FROM python3.10 as ansible
#RUN apt-get install -y sshpass
#RUN pip3 install ansible  ansible-lint  python-debian



