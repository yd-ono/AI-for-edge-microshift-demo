# Simple video stream webserver



```
podman build -t cam -f Containerfile.local .

podman run -ti --privileged --rm -v $(pwd):/app:z -p 5000:5000 cam

```

Open https://localhost:5000
Click on "Link"