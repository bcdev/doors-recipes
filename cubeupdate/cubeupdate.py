from copy import deepcopy
import numpy as np
from typing import Dict

from zappend.api import SliceSource
from zappend.api import zappend

from constants import CHUNK_CONFIGS
from constants import UPDATE_CONFIGS
from constants import S3_BUCKET
from datasetretriever import get_cmems_dataset
from datasetretriever import get_s3_dataset
from slicesources import ChlBaseSliceSource
from slicesources import ChlTimeOptSliceSource
from slicesources import HrocBaseSliceSource1
from slicesources import HrocBaseSliceSource2
from slicesources import HrocBaseSliceSource3
from slicesources import HrocTimeOptSliceSource
from slicesources import SalinityBaseSliceSource
from slicesources import SalinityTimeOptSliceSource
from slicesources import SstBaseSliceSource
from slicesources import SstTimeOptSliceSource

_UPDATE_CONFIGS = UPDATE_CONFIGS.copy()
_SLICE_SOURCE_CONFIGS = {
    "chl": {
        "base_slice_source": ChlBaseSliceSource,
        "time_opt_slice_source": ChlTimeOptSliceSource,
    },
    "sst": {
        "base_slice_source": SstBaseSliceSource,
        "time_opt_slice_source": SstTimeOptSliceSource,
    },
    "salinity": {
        "base_slice_source": SalinityBaseSliceSource,
        "time_opt_slice_source": SalinityTimeOptSliceSource,
    },
    "hroc": {
        "base_slice_sources": {
            0: HrocBaseSliceSource1,
            1: HrocBaseSliceSource2,
            2: HrocBaseSliceSource3,
        },
        "time_opt_slice_source": HrocTimeOptSliceSource,
    },
}
_UPDATE_CONFIGS.update(_SLICE_SOURCE_CONFIGS)

_VAR_CHUNKS_DICT = {
    "*": {"encoding": {"chunks": None}},
    "time": {"dims": ["time"], "encoding": {"chunks": None}},
}


def _get_var_chunks_dict(update_config: Dict, chunks: Dict):
    var_chunks_dict = deepcopy(_VAR_CHUNKS_DICT)
    var_chunks_dict.update(_get_var_chunks(update_config, chunks))
    return var_chunks_dict


def _get_var_chunks(update_config: Dict, chunks: Dict) -> Dict:
    var_dict = {}
    base_var_dict = {
        "dims": list(chunks.keys()),
        "encoding": {"chunks": list(chunks.values()), "dtype": "float32"},
    }
    for base_var in update_config.get("base_variables", []):
        var_dict[base_var] = base_var_dict
    return var_dict


def _update_cubes():
    for dataset_id, update_config in UPDATE_CONFIGS.items():
        _update_base_cube(dataset_id, update_config)
        _update_time_opt_cube(dataset_id, update_config)


def _update_base_cube(dataset_id: str, update_config: Dict):
    if update_config["path_to_base"].endswith(".levels"):
        _update_levels_cube(
            update_config,
            CHUNK_CONFIGS[dataset_id]["base_chunking"],
            _SLICE_SOURCE_CONFIGS[dataset_id]["base_slice_sources"],
        )
    else:
        _update_cube(
            update_config,
            update_config["path_to_base"],
            _SLICE_SOURCE_CONFIGS[dataset_id]["base_slice_source"],
            CHUNK_CONFIGS[dataset_id]["base_chunking"],
        )


def _update_time_opt_cube(dataset_id: str, update_config: Dict):
    _update_cube(
        update_config,
        update_config["path_to_time_opt"],
        _SLICE_SOURCE_CONFIGS[dataset_id]["time_opt_slice_source"],
        CHUNK_CONFIGS[dataset_id]["time_opt_chunking"],
    )


def _update_cube(
    update_config: Dict, path: str, slice_source: SliceSource, chunks: Dict[str, int]
):
    cmems_ds = get_cmems_dataset(update_config, path)
    if cmems_ds is None:
        print("No newer timestamps detected")
        return
    slice_stamps = list(cmems_ds.time.values)
    slice_stamps = [np.datetime_as_string(ss, unit="D") for ss in slice_stamps]

    base_var_chunks_dict = _get_var_chunks_dict(update_config, chunks)
    print(f"Writing to {path}")
    zappend(
        slice_stamps,
        target_dir=f"s3://{S3_BUCKET}/{path}",
        slice_source=slice_source,
        append_dim="time",
        variables=base_var_chunks_dict,
    )


def _update_levels_cube(
    update_config: Dict, chunks: Dict[str, int], slice_sources: Dict[int, SliceSource]
):
    base_path = update_config["path_to_base"]
    cmems_ds = get_cmems_dataset(update_config, base_path)
    if cmems_ds is None:
        print("No newer timestamps detected")
        return
    slice_stamps = list(cmems_ds.time.values)
    slice_stamps = [np.datetime_as_string(ss, unit="D") for ss in slice_stamps]

    num_levels = get_s3_dataset(update_config["path_to_base"]).num_levels

    base_var_chunks_dict = _get_var_chunks_dict(update_config, chunks)
    for n in num_levels:
        path = f"{base_path}/{n}.zarr"
        print(f"Writing to {path}")
        slice_source = slice_sources[n]
        zappend(
            slice_stamps,
            target_dir=f"s3://{S3_BUCKET}/{path}",
            slice_source=slice_source,
            append_dim="time",
            variables=base_var_chunks_dict,
        )


if __name__ == "__main__":
    _update_cubes()
