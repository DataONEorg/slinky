### Docker Images for Slinky
The Kubernetes deployment uses docker images for its pods. Over time,
these images may need to be updated for new features. This folder
contains all of the custom docker files so that they can be rebuilt and
pushed to the web, so that the kubernetes deployment can pull the
updated image.

#### Building, Tagging, & Deploying

For each service, the ultimate goal is to bundle external files inside
the Docker image. These external files range from `requirements.txt` for
container requirements, the `d1lod/` folder for processing code, and
anny scripts that need to be run when the container is started. The
process of building, tagging, and pushing to Docker Hub is the
standard/normal process.

While tagging, be sure to use the correct tag and to _not_ overwrite the
production tag while testing (if this is done, Kubernetes will pull the
test image and deploy it).

Note that _both_ the worker and scheduler images depend on the contents
of d1lod (open the Dockerfile and see for yourself). Docker doesn't
allow directory traversal in its Dockerfiles while copying files/folders
into an image. For this reason, _the prerequisite is that the `d1lod/`
directory is copied into each deployment directory_. For example, before
building the scheduler, copy `slinky/d1lod` so that `scheduler/d1lod/`
exists.


##### worker
The ultimate goal of the worker image is to bundle the
`requirements.txt` and `work.py` script inside the docker image.


##### scheduler
The scheduler image crawls DataONE for content; the code that does this
is in the d1lod root directory. This must be copied into the container
along with the other requirements in the `scheduler/` folder.

##### virtuoso
The Virtuoso Docker build contains the Virtuoso plugin files for
enabling authenticated SPARQL queries. The plugin is copied to
Virtuoso's default plugin directory so that it can be enndabled through
Virtuoso Conductor.
