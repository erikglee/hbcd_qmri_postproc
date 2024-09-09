#The base image is the AMD64 version of centos:centos7.9.2009, which
#should correspond to the OS at MSI
#FROM amd64/centos:7.9.2009
#FROM ubuntu:latest
FROM python:3.9.16-slim-bullseye

# Prepare environment
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    apt-utils \
                    autoconf \
                    build-essential \
                    bzip2 \
                    ca-certificates \
                    curl \
                    gcc \
                    git \
                    gnupg \
                    libtool \
                    lsb-release \
                    pkg-config \
                    unzip \
                    wget \
                    xvfb \
                    default-jre \
                    zlib1g \
                    pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/

#Install relavent python packages
#RUN apt update 
#RUN apt install software-properties-common -y
#RUN add-apt-repository ppa:deadsnakes/ppa -y
#RUN apt update 
#ENV DEBIAN_FRONTEND=noninteractive
#RUN apt install python3.9 -y
#RUN apt-get install -y python3
#RUN apt-get install -y python3-dev
#RUN python3 -m pip install python-dev-tools
RUN python3 -m pip install antspyx==0.4.2
RUN python3 -m pip install numpy==1.22.4 #previously was 1.20.3
RUN python3 -m pip install scipy==1.8.0
RUN python3 -m pip install nibabel==3.2.2
RUN python3 -m pip install matplotlib==3.5.1


#Grab code + colorlut
RUN mkdir /postproc_code
COPY ./postproc_code/ /postproc_code/
#COPY ./postproc_code/run.py /postproc_code
#COPY ./postproc_code/qmri_postproc.py /postproc_code 
#COPY ./postproc_code/FreeSurferColorLUT.txt /postproc_code

#Set permissions
RUN chmod 555 -R /postproc_code

#Add code dir to path
ENV PATH="${PATH}:/postproc_code"
RUN pipeline_name=hbcd_qmri_postproc && cp /postproc_code/run.py /postproc_code/$pipeline_name

ENTRYPOINT ["hbcd_qmri_postproc"]