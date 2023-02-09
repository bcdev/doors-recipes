# Doors Recipes

This repository is dedicated to hosting the scripts/notebooks/files that are 
required in the scope of the DOORS project to create AR Data Cubes from data 
provided by project partners.

There are two folders in this repository: `cubegen` and `docgen`.

`cubegen` contains the functionality to create data cubes from the data
provided by DOORS modelers. 
As this package is subject to change, it is versioned (see the changelog for
differences between versions).
For each model provisioner, there is a dedicated folder which contains a 
script named `create-cube.py`. Each script expects one mandatory and 
one optional parameter.
The mandatory parameter is `input-path`: The path to where on your local 
computer the input data is stored (as xcube currently does not support 
accessing ftp data, this is so far the best solution to access the input data).
The second parameter, `output-path`, allows you to specify an output folder on
your local computer.
If omitted, the resulting cube is written directly to the s3 bucket (this
will only work though if you have valid AWS credentials stored on your 
computer).
As many steps of the cube preparation are the same or similar for the various 
models, there is an utils-package `doorsutils` which contains functions that are 
used more than once.

`docgen` contains a single script that can create human-readable descriptions
of the datasets stored in the s3 bucket.
These descriptions may be used for documentation or in documents.
This code has been tweaked from https://github.com/deepesdl/deepesdl-doc to
also run on xarray datasets.
The single parameter is an optional output path you might indicate to where the
documents shall be written.
If omitted, they are written to the docgen folder.
