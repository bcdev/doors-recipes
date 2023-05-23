from datetime import datetime
import numpy as np
import pandas as pd
from typing import Optional
import xarray as xr

from xcube.core.store import new_data_store
from xcube.core.update import update_dataset_chunk_encoding

from .constants import TIME_FORMAT


def adjust_metadata(ds: xr.Dataset, contributor_data: dict) -> xr.Dataset:
    version = ''
    with open('../version.py', 'r') as v:
        version = str(v.read())
    if 'file_name' in ds.attrs:
        ds.attrs['orig_file_name'] = ds.attrs.pop('file_name')
    if 'file' in ds.attrs:
        ds.attrs['orig_file_name'] = ds.attrs.pop('file')
    if 'title' in ds.attrs:
        ds.attrs['title'] = \
            f'DOORS {contributor_data["name"]} {ds.attrs["title"]}'
    ds.attrs['recipe'] = contributor_data['recipe_path']
    ds.attrs['date_modified'] = datetime.now().strftime(TIME_FORMAT)
    if 'lon' in ds:
        ds.attrs['geospatial_lon_min'] = ds.lon[0].values
        ds.attrs['geospatial_lon_max'] = ds.lon[-1].values
    if 'lat' in ds:
        first = ds.lat[0].values
        last = ds.lat[-1].values
        if first < last:
            ds.attrs['geospatial_lat_min'] = first
            ds.attrs['geospatial_lat_max'] = last
        else:
            ds.attrs['geospatial_lat_min'] = last
            ds.attrs['geospatial_lat_max'] = first
    if 'time' in ds:
        ds.attrs['time_coverage_start'] = get_formatted_time(ds.time[0].values)
        ds.attrs['time_coverage_end'] = get_formatted_time(ds.time[-1].values)
        time_period = _determine_time_period(ds)
        if time_period is not None:
            ds.attrs['time_period'] = time_period
    ds.attrs['acknowledgment'] = 'DOORS project'
    ds.attrs['project'] = 'DOORS'
    ds.attrs['contributor_name'] = contributor_data['name']
    ds.attrs['contributor_url'] = contributor_data['url']
    ds.attrs['creator_name'] = 'Brockmann Consult GmbH'
    ds.attrs['creator_url'] = 'www.brockmann-consult.de'
    ds.attrs['creator_email'] = 'info@brockmann-consult.de'
    ds.attrs['doors_cube_gen_version'] = version
    return ds


def get_input_store(input_path: str):
    return new_data_store(
        'file',
        root=input_path
    )


def get_output_store(output_path: str, contributor: str):
    if output_path:
        return new_data_store(
            'file',
            root=output_path
        )
    return new_data_store(
        's3',
        root=f'doors-cubes/model-data/{contributor}',
        storage_options={
            'anon': False
        }
    )


def get_formatted_time(time) -> str:
    return pd.to_datetime(time).strftime(TIME_FORMAT)


def rechunk(ds: xr.Dataset, chunk_sizes: dict) -> xr.Dataset:
    for data_var in ds.data_vars:
        for dim_name, dim_chunk_size in chunk_sizes.items():
            if dim_name in ds[data_var].dims:
                ds[data_var] = \
                    ds[data_var].chunk(chunks={dim_name: dim_chunk_size})
    ds = update_dataset_chunk_encoding(
        ds,
        chunk_sizes=chunk_sizes,
        format_name='zarr'
    )
    return ds


def _determine_time_period(ds: xr.Dataset) -> Optional[str]:
    if len(ds['time'] == 1):
        return
    time_diff = ds['time'].diff(dim=ds['time'].dims[0]).\
        values.astype(np.float64)
    time_res = time_diff[0]
    time_regular = np.allclose(time_res, time_diff, 1e-8)
    if time_regular:
        time_period = pd.to_timedelta(time_res).isoformat()
        # remove leading P
        time_period = time_period[1:]
        # removing sub-day precision
        day_precision, sub_day_precision = time_period.split('T')
        if day_precision != '0D':
            return day_precision
        if '0M0S' in sub_day_precision:
            return sub_day_precision[:-4]
        elif '0S' in sub_day_precision:
            return sub_day_precision[:-2]
        return sub_day_precision
