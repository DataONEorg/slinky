FROM tenforce/virtuoso:1.3.2-virtuoso7.2.0

RUN apt-get update

# Copy the ods plugin into Virtuoso's default plugins directory (change this in virtuoso.ini)
COPY ods_framework_dav.vad /usr/local/virtuoso-opensource/share/virtuoso/vad/ods_framework_dav.vad
