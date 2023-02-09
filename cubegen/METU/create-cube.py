import numpy as np
import sys
import xarray as xr

import cubegen.doorsutils.utils as du


CHUNK_SIZES={'time': 1, 'deptht': 1}
CONTRIBUTOR_DATA = dict(
    name='METU',
    url='https://www.metu.edu.tr/',
    recipe_path='https://github.com/bcdev/doors-recipes/cubegen/METU'
)


def _rename_spatial_coords(ds: xr.Dataset) -> xr.Dataset:
    if 'x' in ds.dims and 'y' in ds.dims:
        ds = ds.rename_dims({'x': 'lon', 'y': 'lat'})
    if 'nav_lat' in ds.coords:
        ds = ds.assign_coords(lat=np.swapaxes(ds.nav_lat.values, 0, 1)[0])
        ds.lat.attrs = ds.nav_lat.attrs
        ds.drop_vars(['nav_lat'])
    if 'nav_lon' in ds.coords:
        ds = ds.assign_coords(lon=ds.nav_lon.values[0])
        ds.lon.attrs = ds.nav_lon.attrs
        ds.drop_vars(['nav_lon'])
    return ds


def _rename_other_coords(ds: xr.Dataset) -> xr.Dataset:
    if 'z' in ds.dims:
        ds = ds.rename(dict(z='deptht'))
        ds = ds.assign_coords(deptht=ds.depth)
    return ds


def _rename_temporal_coords(ds: xr.Dataset) -> xr.Dataset:
    if 'time_counter' in ds.dims:
        ds = ds.rename(dict(time_counter='time'))
        ds = ds.assign_coords(time_counter=ds.time)
    return ds


def _mask_data(ds: xr.Dataset, mask: xr.Dataset) -> xr.Dataset:
    masked_ds = xr.merge([ds, mask])
    vars_dict = dict()
    for data_var in masked_ds.data_vars:
        if 'time' in masked_ds[data_var].dims and \
                'deptht' in masked_ds[data_var].dims and \
                'lat' in masked_ds[data_var].dims and \
                'lon' in masked_ds[data_var].dims:
            masked_array = \
                xr.where(
                masked_ds.mask == 1, masked_ds[data_var], np.nan).\
                    transpose("time", "deptht", "lat", "lon"
            )
            masked_array.attrs = ds[data_var].attrs
            vars_dict[data_var] = masked_array
    masked_ds = masked_ds.assign(vars_dict)
    masked_ds = masked_ds.drop_vars(['mask', 'latitude', 'longitude', 'depth'])
    return masked_ds


def _prepare_dataset(ds: xr.Dataset) -> xr.Dataset:
    ds = du.rechunk(ds, CHUNK_SIZES)
    ds = _rename_spatial_coords(ds)
    ds = _rename_temporal_coords(ds)
    ds = _rename_other_coords(ds)
    ds = du.adjust_metadata(ds, CONTRIBUTOR_DATA)
    return ds


def _create_cube(input_path: str, output_path: str = None):
    input_store = du.get_input_store(input_path)
    output_store = du.get_output_store(output_path, CONTRIBUTOR_DATA['name'])

    fs_type = 's3' if output_path is None else 'file'

    mask_ds = input_store.open_data('mask.nc')
    mask_ds = _prepare_dataset(mask_ds)

    for data_id in input_store.get_data_ids():
        if 'BlackSea' not in data_id:
            continue
        ds = input_store.open_data(data_id)
        ds = _prepare_dataset(ds)
        ds = _mask_data(ds, mask_ds)
        ds_id = data_id.split('.nc')[0]
        print(f'Writing {ds_id}')
        output_store.write_data(
            ds, f'{ds_id}.levels', replace=True,
            writer_id=f'dataset:levels:{fs_type}'
        )


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        raise ValueError('Expected input_path and optionally output_path')
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) == 3 else None
    _create_cube(input_path, output_path)
