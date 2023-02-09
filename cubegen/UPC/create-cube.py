import sys
import xarray as xr

from xcube.core.gridmapping import GridMapping
from xcube.core.resampling import resample_in_space

import cubegen.doorsutils.utils as du

CHUNK_SIZES = {'s_rho': 1}
CONTRIBUTOR_DATA = dict(
    name='UPC',
    url='https://www.upc.edu/en',
    recipe_path='https://github.com/bcdev/doors-recipes/cubegen/UPC'
)
NAMES = ['rho', 'u', 'v', 'psi']


def _adjust_metadata(ds: xr.Dataset, name: str) -> xr.Dataset:
    ds.attrs['title'] = f'{ds.attrs["title"]} {name}'
    return ds


def _get_subset(ds: xr.Dataset, name: str) -> xr.Dataset:
    drop_list = []
    for var in ds.data_vars:
        if f'lon_{name}' not in ds[var].coords or \
                f'lat_{name}' not in ds[var].coords:
            drop_list.append(var)
    ds_sub = ds.drop_vars(drop_list)
    drop_coords_list = [coord for coord in ds.coords]
    for var in ds_sub.data_vars:
        for coord in ds_sub[var].coords:
            if coord in drop_coords_list:
                drop_coords_list.remove(coord)
    return ds_sub.drop_vars(drop_coords_list)


def _rename_temporal_coords(ds: xr.Dataset) -> xr.Dataset:
    if 'ocean_time' in ds.dims:
        ds = ds.rename(dict(ocean_time='time'))
        ds = ds.assign_coords(ocean_time=ds.time)
        ds = ds.drop_vars('ocean_time')
    return ds


def _resample_to_regular(ds: xr.Dataset) -> xr.Dataset:
    gm = GridMapping.from_dataset(ds)
    new_gm = gm.to_regular()
    return resample_in_space(ds, target_gm=new_gm)


def _create_cube(input_path: str, output_path: str = None):
    input_store = du.get_input_store(input_path)
    output_store = du.get_output_store(output_path, CONTRIBUTOR_DATA['name'])

    fs_type = 's3' if output_path is None else 'file'

    # As the input datasets hold different spatial variables,
    # we will split it up into subset cubes
    for data_id in input_store.get_data_ids():
        ds = input_store.open_data(data_id)
        for name in NAMES:
            ds_subset = _get_subset(ds, name)
            ds_subset = _resample_to_regular(ds_subset)
            ds_subset = _rename_temporal_coords(ds_subset)
            ds_subset = du.rechunk(ds_subset, CHUNK_SIZES)
            ds_subset = du.adjust_metadata(ds_subset, CONTRIBUTOR_DATA)
            ds_subset = _adjust_metadata(ds_subset, name)

            ds_id = f'{data_id.split(".nc")[0]}_{name}'
            output_store.write_data(
                ds_subset,
                f'{ds_id}.levels',
                replace=True,
                writer_id=f'dataset:levels:{fs_type}'
            )


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        raise ValueError('Expected input_path and optionally output_path')
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) == 3 else None
    _create_cube(input_path, output_path)
