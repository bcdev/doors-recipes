from typing import Dict
import xarray as xr

from xcube.core.store import new_data_store
from zappend.api import SliceSource

from constants import CHUNK_CONFIGS
from constants import UPDATE_CONFIGS

_STORE = new_data_store("cmems")
_DATASETS = dict()


def _get_dataset(dataset_id: str, update_config: Dict):
    if dataset_id not in _DATASETS:
        data_id = update_config["CMEMS_store_data_id"]
        _DATASETS[dataset_id] = _STORE.open_data(data_id)
    return _DATASETS[dataset_id]


class CmemsSliceSource(SliceSource):
    def __init__(self, dataset_id: str, update_config: Dict, chunks: Dict, timestamp: str):
        self._dataset_id = dataset_id
        self._update_config = update_config
        self._chunks = chunks
        self._timestamp = timestamp
        self._data_set = None

    def get_dataset(self) -> xr.Dataset:
        self._data_set = _get_dataset(self._dataset_id, self._update_config)
        self._data_set = self._data_set.sel(time=self._timestamp, method="nearest")
        self._data_set = self._rename_vars(self._data_set, self._update_config)
        self._data_set = self._subset_vars(self._data_set, self._update_config)
        self._data_set = self._adjust_dtype(self._data_set, self._update_config)
        self._data_set = self._reduce_dim(self._data_set, self._update_config)
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
        for var_name, dtype in update_config.get("dtype_adjustments", {}):
            ds[var_name] = ds[var_name].astype(dtype)
        return ds

    @staticmethod
    def _reduce_dim(ds: xr.Dataset, update_config: Dict) -> xr.Dataset:
        for dim_name, dim_index in update_config:
            ds = ds.isel({dim_name: dim_index})
            ds = ds.drop_vars(dim_name)
            ds = ds.drop_dims(dim_name)
        return ds

    @staticmethod
    def _add_attributes(ds: xr.Dataset, update_config: Dict) -> xr.Dataset:
        ds.attrs["title"] = update_config["title"]
        ds.attrs["base_dataset"] = update_config["CMEMS_base_dataset"]
        ds.attrs["base_data_id"] = update_config["CMEMS_store_data_id"]
        for attr_name, attr_value in update_config.get("additional_attrs", {}):
            ds.attrs[attr_name] = attr_value
        for var_name, attr_dict in update_config.get("additional_var_attrs", {}):
            for attr_name, attr_value in attr_dict:
                ds[var_name].attrs[attr_name] = attr_value
        return ds

    @staticmethod
    def _chunk_ds(ds: xr.Dataset, chunks: Dict) -> xr.Dataset:
        for var_name in ds.data_vars:
            if var_name != "crs":
                if ('time' in ds[var_name].dims and
                        'lat' in ds[var_name].dims and
                        'lon' not in ds[var_name].dims):
                    ds[var_name] = ds[var_name].chunk(chunks)
        return ds

    def close(self):
        if self._data_set is not None:
            self._data_set.close()


class ChlBaseSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            "chl",
            UPDATE_CONFIGS["chl"],
            CHUNK_CONFIGS["chl"]["base_chunking"],
            timestamp
        )


class ChlTimeOptSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            "chl",
            UPDATE_CONFIGS["chl"],
            CHUNK_CONFIGS["chl"]["time_opt_chunking"],
            timestamp
        )


class SstBaseSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            "sst",
            UPDATE_CONFIGS["sst"],
            CHUNK_CONFIGS["sst"]["base_chunking"],
            timestamp
        )


class SstTimeOptSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            "sst",
            UPDATE_CONFIGS["sst"],
            CHUNK_CONFIGS["sst"]["time_opt_chunking"],
            timestamp
        )


class SalinityBaseSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            "salinity",
            UPDATE_CONFIGS["salinity"],
            CHUNK_CONFIGS["salinity"]["base_chunking"],
            timestamp
        )


class SalinityTimeOptSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            "salinity",
            UPDATE_CONFIGS["salinity"],
            CHUNK_CONFIGS["salinity"]["time_opt_chunking"],
            timestamp
        )


class HrocBaseSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["hroc"],
            CHUNK_CONFIGS["hroc"]["base_chunking"],
            timestamp
        )


class HrocTimeOptSliceSource(CmemsSliceSource):
    def __init__(self, timestamp: str):
        super().__init__(
            UPDATE_CONFIGS["hroc"],
            CHUNK_CONFIGS["hroc"]["time_opt_chunking"],
            timestamp
        )
