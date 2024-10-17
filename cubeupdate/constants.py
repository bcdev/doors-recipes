CHL_DATA_ID = "cmems_obs-oc_blk_bgc-plankton_my_l4-gapfree-multi-1km_P1D"
HROC_DATA_ID = "cmems_obs_oc_blk_bgc_tur-spm-chl_nrt_l4-hr-mosaic_P1D-m"
SALINITY_DATA_ID = "cmems_mod_blk_phy-sal_anfc_2.5km_P1D-m"
SST_DATA_ID = "cmems_SST_BS_SST_L4_REP_OBSERVATIONS_010_022"

CHUNK_CONFIGS = {
    "chl": {
        "base_chunking": {
            "time": 1,
            "lat": 200,
            "lon": 321
        },
        "time_opt_chunking": {
            "time": 113,
            "lat": 158,
            "lon": 367
        }
    },
    "sst": {
        "base_chunking": {
            "time": 1,
            "lat": 200,
            "lon": 321
        },
        "time_opt_chunking": {
            "time": 100,
            "lat": 200,
            "lon": 321
        }
    },
    "salinity": {
        "base_chunking": {
            "time": 1,
            "lat": 261,
            "lon": 591
        },
        "time_opt_chunking": {
            "time": 155,
            "lat": 87,
            "lon": 197
        }
    },
    "hroc": {
        "base_chunking": {
            "time": 1,
            "lat": 2160,
            "lon": 1512
        },
        "time_opt_chunking": {
            "time": 1704,
            "lat": 60,
            "lon": 56
        }
    }
}

UPDATE_CONFIGS = {
    "chl": {
        "title": "CMEMS CHL Black Sea",
        "path_to_base": "CMEMS_CHL_1x790x1101_v3.zarr",
        "path_to_time_opt": "CMEMS_CHL_113x158x367_v3.zarr",
        "CMEMS_base_dataset": "OCEANCOLOUR_BLK_BGC_L4_MY_009_154",
        "CMEMS_store_data_id": CHL_DATA_ID,
        "renamings": {
            "lat": "latitude",
            "lon": "longitude"
        },
        "base_variables": ["chl"]
    },
    "sst": {
        "title": "CMEMS SST Black Sea",
        "path_to_base":
            "CMEMS_SST_BS_SST_L4_REP_OBSERVATIONS_010_022_1x200x321_v4.zarr",
        "path_to_time_opt":
            "CMEMS_SST_BS_SST_L4_REP_OBSERVATIONS_010_022_100x200x321_v4.zarr",
        "CMEMS_base_dataset": "SST_BS_SST_L4_REP_OBSERVATIONS_010_022",
        "CMEMS_store_data_id": SST_DATA_ID,
        "renamings": {
            "lat": "latitude",
            "lon": "longitude"
        },
        "var_subsets": ["analysed_sst"],
        "dtype_adjustments": {
            "analysed_sst": "float32"
        },
        "base_variables": ["analysed_sst"]
    },
    "salinity": {
        "title": "CMEMS Salinity Black Sea Analysis and Forecast",
        "path_to_base": "CMEMS_SAL_BS_Forecast-1x261x591_v4.zarr",
        "path_to_time_opt": "CMEMS_SAL_BS_Forecast-155x87x197_v4.zarr",
        "CMEMS_base_dataset": "BLKSEA_ANALYSISFORECAST_PHY_007_001",
        "CMEMS_store_data_id": SALINITY_DATA_ID,
        "dimensionality_reduction": {
            "depth": 0
        },
        "additional_attrs": {
            "depth": 0.5002
        },
        "additional_var_attrs": {
            "so": {
                "depth": 0.5002
            }
        },
        "base_variables": ["so"]
    },
    "hroc": {
        "title": "HR-OC Coastal Monthly Black Sea",
        "path_to_base": "CMEMS_OC_HR_BS-1x2160x1512_v1.zarr",
        "path_to_time_opt": "CMEMS_OC_HR_BS-1704x60x56_v1.zarr",
        "CMEMS_base_dataset": "OCEANCOLOUR_BLK_BGC_HR_L4_NRT_009_212",
        "CMEMS_store_data_id": HROC_DATA_ID,
        "base_variables": ["CHL", "SPM", "TUR"]
    }
}
