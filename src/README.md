# Tempora python workshop

## Environment

For this workshop, we will be using temporal cli to start the server.

https://docs.temporal.io/cli

Alternatively, you can use docker-compose

https://github.com/temporalio/docker-compose

## Troubleshooting


## NDE

## Prevent having several temporal workers running with different code versions

It will make difficult to debug the code if you have several workers running with different code versions.


Before starting a new worker run the following command to ensure that no other workers are running  and accidentally 
polling from the same task queue. 
``` bash
# start temporal server 
pkill -f temporal_worker
```





``` bash
# start temporal server 
temporal server start-dev
```








``` bash
# ensure we don't have any old process workers running, with name containing temporal_worker


```

``` bash
# start temporal server https://docs.temporal.io/cli
temporal server start-dev
```
