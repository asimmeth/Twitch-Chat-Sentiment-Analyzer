#! /bin/bash
sudo systemctl daemon-reload
sudo systemctl start flask
sudo systemctl stop nginx
sudo systemctl restart nginx

