import sys

import cubegen.doorsutils.utils as du

CONTRIBUTOR_DATA = dict(
    name='Hereon',
    url='https://hereon.de/',
    recipe_path='https://github.com/bcdev/doors-recipes/cubegen/Hereon'
)


def _create_cube(input_path: str, output_path: str = None):
    input_store = du.get_input_store(input_path)
    output_store = du.get_output_store(output_path, CONTRIBUTOR_DATA['name'])

    fs_type = 's3' if output_path is None else 'file'

    data_ids = list(input_store.get_data_ids())
    data_ids.sort()

    # As currently it is mot possible to update data in a levels format,
    # we first have to write the data to a zarr, then read it back in,
    # and then write it as a levels product
    for i, ds_id in enumerate(data_ids):
        ds = input_store.open_data(ds_id)
        if i == 0:
            output_store.write_data(
                ds,
                'Hereon--WAVES-BSeas4-BS-b20230123_re-sv08.00.zarr',
                replace=True,
                writer_id=f'dataset:zarr:{fs_type}')
        else:
            output_store.write_data(
                ds,
                'Hereon--WAVES-BSeas4-BS-b20230123_re-sv08.00.zarr',
                replace=False,
                append_dim='time',
                writer_id='dataset:zarr:file'
            )
    written_ds = output_store.open_data(
        'Hereon--WAVES-BSeas4-BS-b20230123_re-sv08.00.zarr'
    )
    written_ds = du.adjust_metadata(written_ds, CONTRIBUTOR_DATA)

    output_store.write_data(
        written_ds,
        'Hereon--WAVES-BSeas4-BS-b20230123_re-sv08.00.levels',
        writer_id=f'dataset:levels:{fs_type}'
    )

    output_store.delete_data(
        'Hereon--WAVES-BSeas4-BS-b20230123_re-sv08.00.zarr'
    )


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        raise ValueError('Expected input_path and optionally output_path')
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) == 3 else None
    _create_cube(input_path, output_path)
