#!/bin/bash

docker build . -f Dockerfile -t gcr.io/btc1-233019/unstage:latest

docker push gcr.io/btc1-233019/unstage:latest



    

