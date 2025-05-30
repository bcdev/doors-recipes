CHL_DATA_ID = "cmems_obs-oc_blk_bgc-plankton_my_l4-gapfree-multi-1km_P1D"
HROC_DATA_ID = "cmems_obs_oc_blk_bgc_tur-spm-chl_nrt_l4-hr-mosaic_P1D-m"
SALINITY_REANALYSIS_DATA_ID = "cmems_mod_blk_phy-sal_my_2.5km_P1D-m"
SALINITY_FORECAST_DATA_ID = "cmems_mod_blk_phy-sal_anfc_2.5km_P1D-m"
SALINITY_DATA_ID = "cmems_mod_blk_phy-sal_anfc_2.5km_P1D-m"
SST_DATA_ID = "cmems_SST_BS_SST_L4_REP_OBSERVATIONS_010_022"

CHUNK_CONFIGS = {
    "chl": {
        "base_chunking": {"time": 1, "lat": 790, "lon": 1101},
        "time_opt_chunking": {"time": 113, "lat": 158, "lon": 367},
    },
    "sst": {
        "base_chunking": {"time": 1, "latitude": 200, "longitude": 321},
        "time_opt_chunking": {"time": 100, "latitude": 200, "longitude": 321},
    },
    "salinity_reanalysis": {
        "base_chunking": {"time": 1, "lat": 261, "lon": 591},
        "time_opt_chunking": {"time": 155, "lat": 87, "lon": 197},
    },
    "salinity_forecast": {
        "base_chunking": {"time": 1, "lat": 274, "lon": 591},
        "time_opt_chunking": {"time": 155, "lat": 137, "lon": 197},
    },
    "hroc": {
        "base_chunking": {"time": 1, "lat": 2160, "lon": 1512},
        "time_opt_chunking": {"time": 426, "lat": 60, "lon": 56},
    },
}

UPDATE_CONFIGS = {
    "chl": {
        "title": "CMEMS CHL Black Sea",
        "path_to_base": "CMEMS_CHL_1x790x1101_v3.zarr",
        "path_to_time_opt": "CMEMS_CHL_113x158x367_v3.zarr",
        "CMEMS_base_dataset": "OCEANCOLOUR_BLK_BGC_L4_MY_009_154",
        "CMEMS_store_data_id": CHL_DATA_ID,
        "renamings": {"latitude": "lat", "longitude": "lon"},
        "base_variables": ["CHL"],
        "time_frequency": "D",
    },
    "sst": {
        "title": "CMEMS SST Black Sea",
        "path_to_base": "CMEMS_SST_BS_SST_L4_REP_OBSERVATIONS_010_022_1x200x321_v4.zarr",
        "path_to_time_opt": "CMEMS_SST_BS_SST_L4_REP_OBSERVATIONS_010_022_100x200x321_v4.zarr",
        "CMEMS_base_dataset": "SST_BS_SST_L4_REP_OBSERVATIONS_010_022",
        "CMEMS_store_data_id": SST_DATA_ID,
        "var_subsets": ["analysed_sst"],
        "dtype_adjustments": {"analysed_sst": "float32"},
        "base_variables": ["analysed_sst"],
        "time_frequency": "D",
    },
    "salinity_reanalysis": {
        "title": "CMEMS Salinity Black Sea Reanalysis",
        "path_to_base": "CMEMS_SAL_BS_Reanalysis-1x261x591_v5.zarr",
        "path_to_time_opt": "CMEMS_SAL_BS_Reanalysis-155x87x197_v5.zarr",
        "CMEMS_base_dataset": "BLKSEA_MULTIYEAR_PHY_007_004",
        "CMEMS_store_data_id": SALINITY_REANALYSIS_DATA_ID,
        "renamings": {"latitude": "lat", "longitude": "lon"},
        "dimensionality_reduction": {"depth": 0},
        "additional_attrs": {"depth": 0.5002},
        "additional_var_attrs": {"so": {"depth": 0.5002}},
        "reference_time": "2015-01-01",
        "start_time": "2015-01-01",
        "base_variables": ["so"],
        "time_frequency": "D",
    },
    "salinity_forecast": {
        "title": "CMEMS Salinity Black Sea Analysis and Forecast",
        "path_to_base": "CMEMS_SAL_BS_Forecast-1x274x591_v5.zarr",
        "path_to_time_opt": "CMEMS_SAL_BS_Forecast-155x137x197_v5.zarr",
        "CMEMS_base_dataset": "BLKSEA_ANALYSISFORECAST_PHY_007_001",
        "CMEMS_store_data_id": SALINITY_FORECAST_DATA_ID,
        "renamings": {"latitude": "lat", "longitude": "lon"},
        "dimensionality_reduction": {"depth": 0},
        "additional_attrs": {"depth": 0.5002},
        "additional_var_attrs": {"so": {"depth": 0.5002}},
        "reference_time": "2023-06-01",
        "start_time": "2023-06-01",
        "base_variables": ["so"],
        "time_frequency": "D",
    },
    "hroc": {
        "title": "HR-OC Coastal Daily Black Sea",
        "path_to_base": "CMEMS_OC_HR_BS-1x2160x1512_v2.levels",
        "CMEMS_base_dataset": "OCEANCOLOUR_BLK_BGC_HR_L4_NRT_009_212",
        "CMEMS_store_data_id": HROC_DATA_ID,
        "renamings": {"latitude": "lat", "longitude": "lon"},
        "base_variables": ["CHL", "SPM", "TUR"],
        "time_frequency": "D",
    },
}

S3_BUCKET = "doors-cubes/blacksea"
