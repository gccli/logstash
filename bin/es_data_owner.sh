#!/bin/bash


# 1000 is the user id of elasticsearch container

chown 1000 -R data/es/0/*
chown 1000 -R data/es/1/*
chown 1000 -R data/es/2/*
