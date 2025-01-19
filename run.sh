#!/bin/bash

while true ; do
    sleep 10 
    python BopTestProxy.py 223p_bacnet_model.ttl 19740 3600 --baseurl http://boptest:5000
done
