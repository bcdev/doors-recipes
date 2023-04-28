import os
import sys

from xcube.core.store import new_data_store

import cubegen.doorsutils.utils as du


CONTRIBUTOR_DATA = dict(
    name='PML',
    url='https://www.pml.ac.uk/',
    recipe_path='https://github.com/bcdev/doors-recipes/cubegen/PML'
)


def _get_input_store(host: str, root: str, username: str, password: str):
    storage_options = {
        'host': host,
        'username': username,
        'password': password
    }
    return new_data_store('ftp',
                          root=root,
                          storage_options=storage_options
                          )


def _create_cube(host: str,
                 root: str,
                 username: str,
                 password: str,
                 offset: int,
                 output_path: str = None
                 ):
    k = int(offset / 10) + 1
    outfile = f'out_{k}'
    output_ds = f'c_gls_LWQ300_201604260000_black_OLCI_V1.4.0_owt_{k}.zarr'
    if os.path.exists(outfile):
        print(f'Entry {output_ds} already exists and is complete')
        return

    input_store = _get_input_store(host, root, username, password)
    output_store = du.get_output_store(output_path, CONTRIBUTOR_DATA['name'])

    if output_store.has_data(output_ds):
        print(f'Found incomplete previous entry {output_ds}, will delete')
        output_store.delete_data(output_ds)

    fs_type = 's3' if output_path is None else 'file'

    data_ids = list(input_store.get_data_ids())
    data_ids.sort()

    # As currently it is not possible to update data in a levels format,
    # we first have to write the data to a zarr, then read it back in,
    # and then write it as a levels product
    print(f'Building {output_ds}')
    for i in range(10):
        index = i + offset
        ds_id = data_ids[index]
        print(f'Opening {ds_id}, #{index + 1}')
        ds = input_store.open_data(ds_id)
        print(f'Processing {ds_id}, #{index + 1}')
        if i == 0:
            output_store.write_data(
                ds,
                output_ds,
                replace=True,
                writer_id=f'dataset:zarr:{fs_type}')
        else:
            output_store.write_data(
                ds,
                output_ds,
                replace=False,
                append_dim='time',
                writer_id='dataset:zarr:file'
            )
    with open(outfile, 'w+') as out:
        out.write('written!')


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 7:
        raise ValueError('Expected host, root, username, password, offset, '
                         ' and optionally output_path')
    host = sys.argv[1]
    root = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]
    offset = int(sys.argv[5])
    output_path = sys.argv[6] if len(sys.argv) == 7 else None
    _create_cube(host, root, username, password, offset, output_path)