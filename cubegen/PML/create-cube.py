import subprocess
import sys
import time

from xcube.core.store import new_data_store

import cubegen.doorsutils.utils as du


CHUNK_SIZES = {'time': 10, 'lat': 512, 'lon': 434}
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
                 output_path: str = None
                 ):
    input_store = _get_input_store(host, root, username, password)

    data_ids = list(input_store.get_data_ids())

    # As currently it is not possible to update data in a levels format,
    # we first have to write the data to a zarr, then read it back in,
    # and then write it as a levels product
    for j in range(270, len(data_ids), 10):
        sub_command = ["python", "create-sub-cube.py",
                        f'{host}', f'{root}',
                        f'{username}', f'{password}',
                        f'{j}']
        if output_path is not None:
            sub_command.append(f'{output_path}')
        subprocess.run(sub_command)

    output_store = du.get_output_store(output_path, CONTRIBUTOR_DATA['name'])
    data_ids = output_store.list_data_ids()
    data_ids.sort()

    fs_type = 's3' if output_path is None else 'file'

    for i, data_id in enumerate(data_ids):
        print(f'Opening {data_id} ...')
        written_ds = output_store.open_data(data_id)
        written_ds = du.adjust_metadata(written_ds, CONTRIBUTOR_DATA)
        written_ds = du.rechunk(written_ds, chunk_sizes=CHUNK_SIZES)
        print(f'Appending {data_id} ...')
        if i == 0:
            output_store.write_data(
                written_ds,
                'c_gls_LWQ300_black_OLCI_V1.4.0_owt.zarr',
                replace=True,
                writer_id=f'dataset:zarr:{fs_type}')
        else:
            output_store.write_data(
                written_ds,
                'c_gls_LWQ300_black_OLCI_V1.4.0_owt.zarr',
                replace=False,
                append_dim='time',
                writer_id='dataset:zarr:file'
            )

    print('Convert to levels')

    final_zarr_ds = output_store.open_data(
        'c_gls_LWQ300_black_OLCI_V1.4.0_owt.zarr'
    )

    output_store.write_data(
        final_zarr_ds,
        'c_gls_LWQ300_201604260000_black_OLCI_V1.4.0_owt.levels',
        writer_id=f'dataset:levels:{fs_type}'
    )

    output_store.delete_data(
        'c_gls_LWQ300_201604260000_black_OLCI_V1.4.0_owt.zarr'
    )


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 6:
        raise ValueError('Expected host, root, username, password,'
                         ' and optionally output_path')
    host = sys.argv[1]
    root = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]
    output_path = sys.argv[5] if len(sys.argv) == 6 else None
    _create_cube(host, root, username, password, output_path)