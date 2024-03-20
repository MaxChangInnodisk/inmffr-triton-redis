# Triton-Redis
Triton server with Redis

## Build Binary File
```bash
docker run --gpus=1 \
--name build-triton-redis \
-it --rm --net=host \
-w /inno \
-v "$(pwd):/inno" \
nvcr.io/nvidia/tritonserver:23.11-py3 \
pip install -U pyinstaller redis && pyinstaller -F redis_heartbeat.py
```

## Verify
* Launch Testing Server
    ```bash
    docker run --gpus=1 \
    --name build-triton-redis \
    -it --rm --net=host \
    -w /inno \
    -v ./dist/redis_heartbeat:/inno/redis_heartbeat \
    nvcr.io/nvidia/tritonserver:23.11-py3 \
    /inno/redis_heartbeat \
    --redis-port 8786 --redis-password admin --triton-port 8788 --process-uuid test
    ```
* Launch Binary File
    ```bash
    docker exec -it build-triton-redis python3 -m http.server 8788
    ```