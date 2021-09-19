# #!/bin/bash

kubectl --context "gke_btc1-233019_us-central1-c_btc2-dev" \
    run unstager-test \
    --rm \
    -i \
    --restart "Never" \
    --image "gcr.io/btc1-233019/unstage:latest" \
    --image-pull-policy "Always" \
    --serviceaccount "unstage"\
    --env="DB_USER=root" \
    --env="DB_HOST=devdb-int.stg.rezfusion.com" \
    --env="DB_PASSWORD=DXtUqdOg5L" \
    --env="REDIS_HOST=redis-master.redis.svc.cluster.local" \
    --command -- python unstage-pr-site.py $1 $2 $3 $4 $5
    

