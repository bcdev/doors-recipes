import sys
import xarray as xr

import cubegen.doorsutils.utils as du

CHUNK_SIZES={'time': 3}
CONTRIBUTOR_DATA = dict(
    name='ISMAR-CNR',
    url='http://www.ismar.cnr.it/',
    recipe_path='https://github.com/bcdev/doors-recipes/cubegen/ISMAR-CNR'
)


def _apply_level(ds: xr.Dataset) -> xr.Dataset:
    return ds.assign(level=[0.01 * i for i in range(len(ds.level))])


def _adjust_metadata(ds: xr.Dataset, data_id: str) -> xr.Dataset:
    if '_hydro_' in data_id:
        ds.attrs['title'] = 'Western BS Hydro 3D Characterization'
    if '_ts_' in data_id:
        ds.attrs['title'] = 'Western BS TS 3D Characterization'
    return ds


def _create_cube(input_path: str, output_path: str = None):
    input_store = du.get_input_store(input_path)
    output_store = du.get_output_store(output_path, CONTRIBUTOR_DATA['name'])

    fs_type = 's3' if output_path is None else 'file'

    for data_id in input_store.get_data_ids():
        if 'unstruct' in data_id:
            # we do not handle unstructured data at the moment
            continue
        ds = input_store.open_data(data_id)
        ds = _apply_level(ds)
        ds = du.rechunk(ds, CHUNK_SIZES)
        ds = du.adjust_metadata(ds, CONTRIBUTOR_DATA)
        ds = _adjust_metadata(ds, data_id)
        ds_id = data_id.split('.nc')[0]
        output_store.write_data(
            ds,
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
