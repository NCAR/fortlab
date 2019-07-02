..  -*- coding: utf-8 -*-

===============
netcdfread task
===============

version: 0.1.0

Read a Netcdf data file and convert data to a Python dictionary

'netcdfread' tasks read a data file in netcdf format and convert data in
the file to a Python dictionary

Command-line syntax
-------------------

usage: pyloco netcdfread.py [-h] [--general-arguments] data 

Read a Netcdf data file and convert data to a Python dictionary

positional arguments:
  data                  netcdf data file

optional arguments:
  -h, --help            show this help message and exit
  --general-arguments   Task-common arguments. Use --verbose to see a list of general arguments

forward output variables:
   data                 Netcdf data in Python dictionary


Examples
---------
