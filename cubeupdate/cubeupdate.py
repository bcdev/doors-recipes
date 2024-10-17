from copy import deepcopy
import numpy as np
from typing import Dict

from xcube.core.store import new_data_store
from zappend.api import zappend

from constants import CHUNK_CONFIGS
from constants import UPDATE_CONFIGS

from slicesources import ChlBaseSliceSource
from slicesources import ChlTimeOptSliceSource
from slicesources import HrocBaseSliceSource
from slicesources import HrocTimeOptSliceSource
from slicesources import SalinityBaseSliceSource
from slicesources import SalinityTimeOptSliceSource
from slicesources import SstBaseSliceSource
from slicesources import SstTimeOptSliceSource


_UPDATE_CONFIGS = UPDATE_CONFIGS.copy()
_SLICE_SOURCE_CONFIGS = {
    "chl": {
        "base_slice_source": ChlBaseSliceSource,
        "time_opt_slice_source": ChlTimeOptSliceSource
    },
    "sst": {
        "base_slice_source": SstBaseSliceSource,
        "time_opt_slice_source": SstTimeOptSliceSource
    },
    "salinity": {
        "base_slice_source": SalinityBaseSliceSource,
        "time_opt_slice_source": SalinityTimeOptSliceSource
    },
    "hroc": {
        "base_slice_source": HrocBaseSliceSource,
        "time_opt_slice_source": HrocTimeOptSliceSource
    }
}
_UPDATE_CONFIGS.update(_SLICE_SOURCE_CONFIGS)

_S3_BUCKET = "doors-cubes/blacksea"
_S3_STORE = new_data_store(
    's3',
    root=_S3_BUCKET,
    storage_options={
        'anon': False
    }
)

_CMEMS_STORE = new_data_store("cmems")

_VAR_CHUNKS_DICT = {
    "*": {
        "encoding": {
            "chunks": None
        }
    },
    "time": {
        "dims": ["time"],
        "encoding": {
            "chunks": None
        }
    }
}


def _get_var_chunks_dict(update_config: Dict, chunks: Dict):
    var_chunks_dict = deepcopy(_VAR_CHUNKS_DICT)
    var_chunks_dict.update(_get_var_chunks(update_config, chunks))
    return var_chunks_dict


def _get_var_chunks(update_config: Dict, chunks: Dict) -> Dict:
    var_dict = {}
    base_var_dict = {
        "dims": ["time", "lat", "lon"],
            "encoding": {
                "chunks": list(chunks.values()),
                "dtype": "float32"
            }
    }
    for base_var in update_config.get("base_variables", []):
        var_dict[base_var] = base_var_dict
    return var_dict



def _update_cubes():
    for dataset_id, update_config in UPDATE_CONFIGS.items():
        _update_cube(dataset_id, update_config)


def _update_cube(dataset_id: str, update_config: Dict):
    path_to_base = update_config["path_to_base"]
    if path_to_base in _S3_STORE.list_data_ids():
        base_ds = _S3_STORE.open_data(path_to_base)
        last_base_timestamp = np.datetime_as_string(base_ds.time[-1].values, unit="D")
        # last_base_timestamp = base_ds.time[-1].values
        cmems_desc = _CMEMS_STORE.describe_data(
            data_id=update_config["CMEMS_store_data_id"]
        )
        cmems_ds = _CMEMS_STORE.open_data(
            data_id=update_config["CMEMS_store_data_id"],
            time_range=[last_base_timestamp, cmems_desc.time_range[1]]
        )
    else:
        cmems_ds = _CMEMS_STORE.open_data(
            data_id=update_config["CMEMS_store_data_id"]
        )
    slice_stamps = list(cmems_ds.time.values)
    slice_stamps = [np.datetime_as_string(ss, unit="D") for ss in slice_stamps]

    base_slice_source = _SLICE_SOURCE_CONFIGS[dataset_id]["base_slice_source"]
    base_chunks = CHUNK_CONFIGS[dataset_id]["base_chunking"]
    base_var_chunks_dict = _get_var_chunks_dict(update_config, base_chunks)
    zappend(
        slice_stamps,
        target_dir=f"s3://{_S3_BUCKET}/{path_to_base}",
        slice_source=base_slice_source,
        append_dim="time",
        variables=base_var_chunks_dict,
        dry_run=True
    )

    time_opt_slice_source = _SLICE_SOURCE_CONFIGS[dataset_id]["time_opt_slice_source"]
    time_opt_chunks = CHUNK_CONFIGS[dataset_id]["time_opt_chunking"]
    time_opt_var_chunks_dict = _get_var_chunks_dict(update_config, time_opt_chunks)
    zappend(
        slice_stamps,
        target_dir=f"s3://{_S3_BUCKET}/{path_to_base}",
        slice_source=time_opt_slice_source,
        append_dim="time",
        variables=time_opt_var_chunks_dict,
        dry_run=True
    )


if __name__ == "__main__":
    _update_cubes()
