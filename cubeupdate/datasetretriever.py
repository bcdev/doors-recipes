from datetime import datetime
from dateutil.relativedelta import relativedelta

from pandas import Timestamp
from typing import Dict

from xcube.core.store import new_data_store

from constants import S3_BUCKET

_S3_STORE = new_data_store("s3", root=S3_BUCKET, storage_options={"anon": False})

_CMEMS_STORE = new_data_store("cmems")
_CMEMS_DATASETS = dict()


def get_cmems_dataset(update_config: Dict, path: str):
    if path in _CMEMS_DATASETS:
        return _CMEMS_DATASETS[path]
    if path in _S3_STORE.list_data_ids():
        ds = _S3_STORE.open_data(path)
        last_base_timestamp = Timestamp(ds.time[-1].values).to_pydatetime()
        if update_config["time_frequency"] == "D":
            delta = relativedelta(days=1)
        elif update_config["time_frequency"] == "M":
            delta = relativedelta(months=1)
        else:
            raise ValueError(
                f"Unsupported time_frequency: "
                f"{update_config["time_frequency"]}. "
                f"Must be 'D' or 'M'."
            )
        first_expected_timestamp = last_base_timestamp + delta
        cmems_desc = _CMEMS_STORE.describe_data(
            data_id=update_config["CMEMS_store_data_id"]
        )
        last_cmems_timestamp = cmems_desc.time_range[1]
        if first_expected_timestamp < datetime.strptime(
            last_cmems_timestamp, "%Y-%m-%d"
        ):
            first_expected_timestamp = first_expected_timestamp.strftime("%Y-%m-%d")
            _CMEMS_DATASETS[path] = _CMEMS_STORE.open_data(
                data_id=update_config["CMEMS_store_data_id"],
                time_range=[first_expected_timestamp, last_cmems_timestamp],
            )
        else:
            _CMEMS_DATASETS[path] = None
    else:
        _CMEMS_DATASETS[path] = _CMEMS_STORE.open_data(
            data_id=update_config["CMEMS_store_data_id"]
        )
    return _CMEMS_DATASETS[path]
