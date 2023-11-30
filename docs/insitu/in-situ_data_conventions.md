# In-Situ Data Conventions

This page explains the requirements for data to be ingested into the DOORS 
System of Systems (SoS). 
To be exact, the data is ingested into the geoDB, from where it can be accessed
by other systems, such as the viewer, the dashboard, or the jupyter lab.
Meeting the requirements listed here ensures that the data is optimally 
supported by the SoS.

These requirements apply to in-situ data, i.e., to data that can be represented
by a spatial feature or feature collection, in most cases a simple point.
If you are dealing with gridded data, please refer to the 
[xcube Dataset Conventions
](https://xcube.readthedocs.io/en/latest/cubespec.html).

## Basic geoDB Concepts

In DOORS, in-situ data is kept within the xcube geoDB. 
The geoDB is a geospatial database designed to store, manipulate, and share 
vector data.
It manages data in the form of collections, where a collection corresponds to
a PostGRES-database table with a geometry.

A collection consists of properties, which correspond to the columns of a csv 
file or the attributes of a shape file.
Each property is defined by a name and a data type.

## Input Data Requirements

### General

- Data should be provided in a file format that can be read in with the 
  geopandas python package (e.g., ESRI shapefile or csv).
- Unless you are not using the default WGS84 system, it is necessary to specify 
  the crs. 
  This does not have to be in the table but should be specified when creating 
  the collection in geodb.
- In case your data is not written using `utf-8` encoding, you'll need to 
  specify which encoding you use when the file is read in.
- The data must not include a column named `id`. 
  Such a column is created by the geoDB and required internally.
  In case your data has such a column, consider renaming it.
- Have a clear and consistent data type for each column / attribute. 
  Data types might need to be explicitly set during geodb ingestion.
- In case you have no-data, please use 'NaN' rather than 'nan'.
- To further group data entries in, e.g., the viewer, you may specify a grouping
  label. For instance, if you have measurements from multiple stations in the 
  same dataset, you may have column/attribute 'station' and assign the name of
  the station to the entry.
- Likewise, you may optionally include text labels to uniquely identify entries.
  Label and group properties are not mutually exclusive.

### Geometry Requirements

- The input data must contain spatial information per entry.
These can come in the form of a geometry defined 
  - either in WKT format (e.g., POINT (28.37510 43.19370) )
  - or columns specifying the coordinate axes of a crs (for example, input data 
    may define columns 'latitude' and 'longitude', so points can be determined 
    from it).
- A geometry must not be 3-dimensional.
- When providing a geometry column, it must be named `geometry`.

### Temporal Requirements

The geoDB itself does not pose restrictions on the way time information is 
stored, however, other parts of the SoS do.
We suggest to have a dedicated column to hold the date, and, if applicable,
the time of day.
In general, any time format is acceptable that might be converted to a pandas 
datetime object.
Examples for acceptable formats for temporal information are:
- 'yyyy-mm-dd hh:mm:dd', e.g., '2023-11-08 13:35:50'
- 'yyyy-mm-dd', e.g., '2023-11-08'
If you do not specify date and time in the same column (but rather in two
different columns) the system of systems currently will only recognise one
of them.
To specify your time information, please use any of the following column 
names: ``time`` , ``timestamp``, ``date``, ``datetime``, ``date-time``. 

Anyway, providing temporal information is optional.

### Collection definition

Before data is ingested into the SoS/geoDB, it is first necessary to define and
create a collection.
This collection definition specifies a collection's crs and the names and data
types of its properties.
An example of such a definition is:

>     collections {
>       "my_collection": {
>         "crs": "EPSG:4326",
>         "properties": {
>           "Station": "text",
>           "Label": "text",
>           "Temperature [°C]": "float",
>           "time": "text",
>           "Measurement Count": "integer" 
>         }
>       }
>     }
