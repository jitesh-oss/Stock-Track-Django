#!/bin/bash

while true  
do
    curl http://127.0.0.1:8000/refresh-stocktrack/
    sleep 60 
    curl http://127.0.0.1:8000/status-stocktrack/
    sleep 60
    curl http://127.0.0.1:8000/alerts/refresh-allalerts/
    sleep 60
    curl http://127.0.0.1:8000/alerts/status-alerts/
    sleep 60
done