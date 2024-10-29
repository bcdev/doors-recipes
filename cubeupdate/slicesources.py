import numpy as np
from typing import Dict
import xarray as xr

from xcube.core.gridmapping import GridMapping
from xcube.core.subsampling import get_dataset_agg_methods
from xcube.core.subsampling import subsample_dataset
from zappend.api import SliceSource

from constants import CHUNK_CONFIGS
from constants import UPDATE_CONFIGS

from datasetretriever import get_cmems_dataset


class CmemsSliceSource(SliceSource):
    def __init__(
        self,
        update_config: Dict,
        path: str,
        chunks: Dict,
        timestamp: str,
        level: int = -1,
    ):
        print(f"Processing timestamp {timestamp}")
        self._update_config = update_config
        self._path = path
        self._chunks = chunks
        self._timestamp = timestamp
        self._data_set = None
        self._level = level

    def get_dataset(self) -> xr.Dataset:
        self._data_set = get_cmems_dataset(self._update_config, self._path)
        self._data_set = self._data_set.sel(time=self._timestamp, method="nearest")
        for var in self._data_set.data_vars:
            self._data_set[var] = self._data_set[var].expand_dims("time")
        self._data_set = self._rename_vars(self._data_set, self._update_config)
        self._data_set = self._subset_vars(self._data_set, self._update_config)
        self._data_set = self._adjust_dtype(self._data_set, self._update_config)
        self._data_set = self._reduce_dim(self._data_set, self._update_config)
        self._data_set = self._maybe_convert_times(self._data_set, self._update_config)
        self._data_set = self._subsample_dataset(self._data_set, self._level)
        self._data_set = self._chunk_ds(self._data_set, self._chunks)
        self._data_set = self._add_attributes(self._data_set, self._update_config)
        return self._data_set

    @staticmethod
    def _rename_vars(ds: xr.Dataset, update_config: Dict) -> xr.Dataset:
        return ds.rename(update_config.get("renamings", {}))

    @staticmethod
    def _subset_vars(ds: xr.Dataset, update_config: Dict) -> xr.Dataset:
        if "var_subsets" in update_config:
            ds = ds[update_config["var_subsets"]]
        return ds

    @staticmethod
    def _adjust_dtype(ds: xr.Dataset, update_config: Dict) -> xr.Dataset:
        for var_name, dtype in update_config.get("dtype_adjustments", {}).items():
            ds[var_name] = ds[var_name].astype(dtype)
        return ds

    @staticmethod
    def _reduce_dim(ds: xr.Dataset, update_config: Dict) -> xr.Dataset:
        for dim_name, dim_index in update_config.get(
            "dimensionality_reduction", {}
        ).items():
            ds = ds.isel({dim_name: dim_index})
            ds = ds.drop_vars(dim_name)
        return ds

    @staticmethod
    def _maybe_convert_times(ds: xr.Dataset, update_config: Dict) -> xr.Dataset:
        if update_config.get("reference_time"):
            reference_time = np.datetime64(update_config.get("reference_time"), "D")
            time_in_days = (ds["time"] - reference_time) // np.timedelta64(1, "D")
            ds = ds.assign_coords(time=time_in_days)
            ds["time"].encoding.update(
                {
                    "units": f"days since {update_config.get("reference_time")}",
                    "calendar": "proleptic_gregorian",
                    "dtype": "int64",
                }
            )
        return ds

    @staticmethod
    def _add_attributes(ds: xr.Dataset, update_config: Dict) -> xr.Dataset:
        ds.attrs["title"] = update_config["title"]
        ds.attrs["base_dataset"] = update_config["CMEMS_base_dataset"]
        ds.attrs["base_data_id"] = update_config["CMEMS_store_data_id"]
        for attr_name, attr_value in update_config.get("additional_attrs", {}).items():
            ds.attrs[attr_name] = attr_value
        for var_name, attr_dict in update_config.get(
            "additional_var_attrs", {}
        ).items():
            for attr_name, attr_value in attr_dict.items():
                ds[var_name].attrs[attr_name] = attr_value
        return ds

    @staticmethod
    def _subsample_dataset(ds: xr.Dataset, level: int) -> xr.Dataset:
        if level < 1:
            return ds
        grid_mapping = GridMapping.from_dataset(ds)
        xy_dim_names = grid_mapping.xy_dim_names
        agg_methods = get_dataset_agg_methods(ds, xy_dim_names=xy_dim_names)
        subsample_dataset_kwargs = dict(
            xy_dim_names=xy_dim_names, agg_methods=agg_methods
        )
        return subsample_dataset(
            ds,
            step=2**level,
            **subsample_dataset_kwargs,
        )

    @staticmethod
    def _chunk_ds(ds: xr.Dataset, chunks: Dict) -> xr.Dataset:
        for var_name in ds.data_vars:
            if var_name != "crs":
                if (
                    "time" in ds[var_name].dims
                    and "lat" in ds[var_name].dims
                    and "lon" in ds[var_name].dims
                ):
                    ds[var_name] = ds[var_name].chunk(chunks)
        return ds

    def close(self):
        if self._data_set is not None:
            self._data_set.close()


class ChlBaseSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["chl"],
            UPDATE_CONFIGS["chl"]["path_to_base"],
            CHUNK_CONFIGS["chl"]["base_chunking"],
            timestamp,
        )


class ChlTimeOptSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["chl"],
            UPDATE_CONFIGS["chl"]["path_to_time_opt"],
            CHUNK_CONFIGS["chl"]["time_opt_chunking"],
            timestamp,
        )


class SstBaseSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["sst"],
            UPDATE_CONFIGS["sst"]["path_to_base"],
            CHUNK_CONFIGS["sst"]["base_chunking"],
            timestamp,
        )


class SstTimeOptSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["sst"],
            UPDATE_CONFIGS["sst"]["path_to_time_opt"],
            CHUNK_CONFIGS["sst"]["time_opt_chunking"],
            timestamp,
        )


class SalinityBaseSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["salinity"],
            UPDATE_CONFIGS["salinity"]["path_to_base"],
            CHUNK_CONFIGS["salinity"]["base_chunking"],
            timestamp,
        )


class SalinityTimeOptSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            # "salinity",
            UPDATE_CONFIGS["salinity"],
            UPDATE_CONFIGS["salinity"]["path_to_time_opt"],
            CHUNK_CONFIGS["salinity"]["time_opt_chunking"],
            timestamp,
        )


class HrocBaseSliceSource1(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["hroc"],
            UPDATE_CONFIGS["hroc"]["path_to_base"],
            CHUNK_CONFIGS["hroc"]["base_chunking"],
            timestamp,
            0,
        )


class HrocBaseSliceSource2(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["hroc"],
            UPDATE_CONFIGS["hroc"]["path_to_base"],
            CHUNK_CONFIGS["hroc"]["base_chunking"],
            timestamp,
            1,
        )


class HrocBaseSliceSource3(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["hroc"],
            UPDATE_CONFIGS["hroc"]["path_to_base"],
            CHUNK_CONFIGS["hroc"]["base_chunking"],
            timestamp,
            2,
        )


class HrocTimeOptSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["hroc"],
            UPDATE_CONFIGS["hroc"]["path_to_time_opt"],
            CHUNK_CONFIGS["hroc"]["time_opt_chunking"],
            timestamp,
        )
