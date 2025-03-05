# CMEMS SST Black Sea

## Basic information

<span style="font-size: x-small">Map tiles and Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.</span>

| Parameter | Value |
| ---- | ---- |
| Time range | 20160101T070000Z to 20240508T190000Z |
| Creator | ISMAR - Institute of Marine Sciences (CNR - ISMAR - GOS - Rome) |

[Click here for full dataset metadata.](#full-metadata)

## Variable list

| Variable | Identifier | Units |
| ---- | ---- | ---- |
| [Analysed Sea Surface Temperature](#analysed\_sst) | analysed\_sst | kelvin |

## Full variable metadata

### <a name="analysed_sst"></a>Analysed Sea Surface Temperature

| Field | Value |
| ---- | ---- |
| comment | \[1982\-2018\] Optimal interpolation \(OI\) SST measurements from ESA CCI SST v2\.0, C3S v\.2\.0 and PFV53 |
| long name | Analysed Sea Surface Temperature |
| long\_name | Analysed Sea Surface Temperature |
| source | [Click here for source.](CMEMS_SST_BS_SST_L4_REP_OBSERVATIONS_010_022_1x200x321_v4.zarr-analysed_sst.md) |
| standard\_name | sea\_surface\_temperature |
| time\_coverage\_end | 20240508T190000Z |
| time\_coverage\_start | 20160101T070000Z |
| type | foundation |
| units | kelvin |
| valid\_max | 4500 |
| valid\_min | -300 |

## <a name="full-metadata"></a>Full dataset metadata

| Field | Value |
| ---- | ---- |
| Conventions | CF\-1\.4 |
| DSD\_entry\_id | \-GOS\-L4HRfnd\-BLK |
| Metadata\_Conventions | Unidata Dataset Discovery v1\.0 |
| Scaling\_Equation | \(scale\_factor\*data\) \+ add\_offset |
| acknowledgment | Please acknowledge the use of these data with the following statement: Generated/provided by Copernicus Marine Service and CNR \- ISMAR ROME\. We would also appreciate being informed of any publications\. |
| cdm\_data\_type | grid |
| comment | WARNING: some applications are unable to properly handle byte values\. If Values >127 are encounterd, please subtract 256 |
| copernicusmarine\_version | 1\.0\.0 |
| creator\_email | gsdk@isac\.cnr\.it |
| creator\_name | ISMAR \- Institute of Marine Sciences \(CNR \- ISMAR \- GOS \- Rome\) |
| creator\_url | [http://gosweb\.artov\.isac\.cnr\.it/](http://gosweb.artov.isac.cnr.it/) |
| date\_created | 20200610T223736Z |
| easternmost\_longitude | 42.375 |
| end\_time | 20231231T190000Z |
| file\_quality\_level | 3 |
| gds\_version\_id | v2\.0\.5 |
| geospatial\_lat\_resolution | 0.05000000074505806 |
| geospatial\_lat\_units | degrees\_north |
| geospatial\_lon\_resolution | 0.05000000074505806 |
| geospatial\_lon\_units | degrees\_east |
| history | GOS\-CMEMS processor V4: new version |
| id |   |
| institution | GOS |
| keywords | Oceans > Ocean Temperature > Sea Surface Temperature |
| keywords\_vocabulary | NASA Global Change Master Directory \(GCMD\) Science Keywords |
| license | free registration at Copernicus Marine Service \(http://marine\.copernicus\.eu/web/56\-user\-registration\-form\.php\) |
| metadata\_link | Link to collection metadata record at archive |
| naming\_authority | org\.ghrsst |
| netcdf\_version\_id | 4\.1\.1, build date: JUN 18 2010" |
| northernmost\_latitude | 48.775001525878906 |
| platform | NOAA AVHRR, Metop\-A AVHRR, \(A\)ATSR, Sentinel\-3A SLSTR series of sensors |
| processing\_level | L4 |
| product\_version | 3\.0 |
| project | Copernicus Marine Environment Monitoring Service \(CMEMS\) |
| publisher\_email | servicedesk\.cmems@mercator\-ocean\.eu, gsdk@isac\.cnr\.it |
| publisher\_name | CNR ISMAR GOS \- CMEMS SST\-TAC |
| publisher\_url | [http://marine\.copernicus\.eu/](http://marine.copernicus.eu/) |
| references | A\. Pisano, B\. Buongiorno Nardelli, C\. Tronconi, R\. Santoleri: The new Mediterranean optimally interpolated pathfinder AVHRR SST Dataset \(1982\-2012\)\. /Remote Sensing of Environment\./ 176 \(2016\) 107\-116, doi:10\.1016/j\.rse\.2016\.01\.019; http://pathfinder\.nodc\.noaa\.gov and Casey, K\.S\., T\.B\. Brandon, P\. Cornillon, and R\. Evans: The Past, Present and Future of the AVHRR Pathfinder SST Program, in Oceanography from Space: Revisited, eds\. V\. Barale, J\.F\.R\. Gower, and L\. Alberotanza, Springer, 2010\. DOI: 10\.1007/978\-90\-481\-8681\-5\_16\. |
| sensor | \[1981\-2016\] NOAA AVHRR series of sensors \(NOAA\-07/09/11/12/14/15/16/17/18/19\), ATSR1, ATSR2, \(A\)ATSR, MetopA AVHRR; \[2017\-2018\]  NOAA AVHRR\-19, MetopA AVHRR, SLSTR\-3A |
| software\_version | Copernicus Marine Service HR L4 Processor V\.2 |
| source | \[1982\-2016\] ESA CCI SST v\.2\.0 L3C product \(SST at 0\.2m\); \[2017\-2018\] C3S v\.2\.0 L3C product \(SST at 0\.2m\); \[1982\-2014\]  Pathfinder\-PFV5\.3 L3C product \(SST skin\) |
| southernmost\_latitude | 38.724998474121094 |
| spatial\_resolution | 0\.05 degree |
| standard\_name\_vocabulary | NetCDF Climate and Forecast \(CF\) Metadata Convention |
| start\_time | 20160101T070000Z |
| stop\_time | 19810825T070000Z |
| summary | \[1982\-2018\] Daily gap\-free maps \(L4\) at 0\.05deg\. x 0\.05deg\. horizontal resolution over the Black Sea\. The maps are obtained using nighttime data extracted from ESA CCI SST v\.2\.0, C3S v\.2\.0 and PFV53 data |
| time\_coverage\_end | 20240508T190000Z |
| time\_coverage\_start | 20160101T070000Z |
| title | CMEMS SST Black Sea |
| uuid |   |
| westernmost\_longitude | 26.375 |

