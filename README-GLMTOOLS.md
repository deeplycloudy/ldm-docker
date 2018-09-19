## Architecture

Base repo includes ./etc, ./cron. After cloning, need to create directories
./data, ./queues, and ./logs

For instance, for a large storage pool mounted at /archive with GLM processing set up in /archive/GLM/realtime/, create a new directory ldm

:/archive/GLM/realtime$ ls
docker-startup.README  ldm  ldm-docker

which will have the three needed directories

:/archive/GLM/realtime/ldm$ ls
data  logs  queues

Then within ldm-docker
ln -s /archive/GLM/realtime/ldm/data data
ln -s /archive/GLM/realtime/ldm/queues queues
ln -s /archive/GLM/realtime/ldm/logs logs

So that the needed directories all exist within the ldm-docker repository and can be mapped as described in docker-compose.yml.

### Data external to the LDM container

To use this LDM to serve GLM grids that are processed locally, it is necessary to have access to those data. This is added to docker-compose in the volumes section.

volumes:
      - /archive/GLM/GLM-L2-GRID_G16/:/glm_grid_data



### etc
Change the hostname in registry.xml

Modify netcheck.conf to feed an internal LDM server that can feed the rest of the world. This allows glmtools + LDM to be run on any box, under the assumption that it's easier to send data between boxes within an institutional firewall than to set up multiple boxes with an open port on 388.

Comment out all of the upstream feeds, since for now we poll the public S3 feed.

pqact.conf doesn't need any changes because we are not acting on any received products (for now)

Configure ldmd.conf to allow the server listed in netcheck.conf to request data.

### Running
See the readme shipped with ldm.

Since the Dockerfile copies in some support files, we need to build a custom image
docker build -t ldm-glm .
which is referred to in the docker-compose file

Then start with
    `docker-compose up -d ldm glmtest glmrelampago`
Which should show the ldm-glm, glmtest, and glmrelampago images running with NAMES ldm-prod and glm-conus, glm-relampago. The latter two images are built from the glmtools-docker repository, which has a separate branch with the relampago processing.

You can enter the running LDM container with
    `docker exec -it ldm-prod bash`
