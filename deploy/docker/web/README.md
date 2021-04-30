# deploy/docker/web

The Dockerfile won't build by default because it depends on building the `d1lod` package inside the container but the source for the package is outside this folder.

To build,

```
cp -r ../../../d1lod .
docker build -t slinky_web .
```

This is mainly to work around Docker not preferring to process `ADD` instructions that reference paths above the working directory. This could have also been worked around by building this image from the root and running `build` with the `-f` argument.
