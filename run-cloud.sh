#!/bin/bash

kubectl --context "gke_btc1-233019_us-central1-c_btc2-dev" \
    run unstager-test \
    --rm \
    -i \
    --restart='Never' \
    --image gcr.io/btc1-233019/unstage:latest \
    --image-pull-policy "Always" \
    --command -- "python unstage-cloud-pr-site.py 1041 --no-dry-run" \
    # --env="DB_USER=root" \
    # --env="DB_HOST=devdb-int.stg.rezfusion.com" \
    # --env="DB_PASSWORD=DXtUqdOg5L" \
    # --env="GITHUB_ACCESS_TOKEN=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" \
    # --env="REDIS_HOST=redis-master.redis.svc.cluster.local" \
    

    

    

    