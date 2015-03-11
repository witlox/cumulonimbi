# Use phusion/baseimage as base image. To make your builds reproducible, make
# sure you lock down to a specific version, not to `latest`!
# See https://github.com/phusion/baseimage-docker/blob/master/Changelog.md for
# a list of version numbers.
FROM phusion/baseimage:0.9.16

# Format: MAINTAINER Name <email@addr.ess>
MAINTAINER J. Bertens <johannes.bertens@gmail.com>

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# Install git
RUN apt-get update
RUN apt-get install python-pip -y
RUN apt-get install git -y

# Get the repository
RUN git clone https://github.com/witlox/cumulonimbi.git

# Install the required packages
RUN pip install -r cumulonimbi/requirements.txt

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*