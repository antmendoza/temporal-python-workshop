#!/bin/bash

ps aux | grep temporal_worker

pkill -f temporal_worker