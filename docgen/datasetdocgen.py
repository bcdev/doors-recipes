#!/usr/bin/env python3

"""Generate description in Markdown and map image for a dataset from geojson"""

from typing import Dict, Any
import sys
import re
import os
import matplotlib.pyplot as plt
import cartopy
import cartopy.io.img_tiles
import matplotlib.patches as patches
import xarray as xr

from xcube.core.store import new_data_store


def create_doors_dataset_docs(output_dir: str, key: str):
    doors_store = new_data_store(
        "s3",
        root=f"doors-cubes/{key}",
        max_depth=3,
        storage_options={"anon": False},
    )
    for data_id in doors_store.get_data_ids():
        dataset = doors_store.open_data(data_id)
        try:
            base_dataset = dataset.base_dataset
        except AttributeError:
            base_dataset = dataset
        _create_dataset_doc(base_dataset, data_id, output_dir)


def _create_dataset_doc(dataset: xr.Dataset, data_id: str, output_dir: str):
    basename = data_id.split(".levels")[0].split("/")[-1]
    print(basename)
    output_filename = basename + ".md"
    bbox_image_path = os.path.join(output_dir, basename + ".png")
    with open(os.path.join(output_dir, output_filename), "w") as output:
        props = dataset.attrs
        output.write(f'# {props.get("title", "")}\n\n')
        output.write("## Basic information\n\n")
        output.write(f'![Bounding box map]({basename + ".png"})<br>\n')
        output.write(
            '<span style="font-size: x-small">Map tiles and Data by '
            '<a href="http://openstreetmap.org">OpenStreetMap</a>,'
            " under "
            '<a href="http://www.openstreetmap.org/copyright">'
            "ODbL</a>.</span>\n\n"
        )
        output.write(make_basic_info(props))
        output.write("## Variable list\n\n")
        # output.write(make_variable_list_table(props['variables']))
        output.write(make_variable_list_table(dataset))
        output.write("## Full variable metadata\n\n")
        for variable in dataset.data_vars:
            variable_source_filename = basename + "-" + variable + ".md"
            output.write(
                f'### <a name="{variable}"></a>'
                f'{dataset[variable].attrs.get("long_name")}\n\n'
            )
            output.write(
                make_table(
                    dataset[variable].attrs, source_link=variable_source_filename
                )
            )
        output.write('## <a name="full-metadata"></a>' "Full dataset metadata\n\n")
        output.write(make_table({k: v for k, v in props.items() if k != "variables"}))
    make_map(props, bbox_image_path)


def make_basic_info(props: Dict[str, Any]) -> str:
    """Create a brief summary from a dictionary of dataset properties.

    Args:
        props: dictionary of dataset properties

    Returns:
        Markdown source containing information about the dataset
    """
    return f"| Parameter | Value |\n" f"| ---- | ---- |\n" + (
        f'| Bounding box latitude | {props["geospatial_lat_min"]} to '
        f'{props["geospatial_lat_max"]} |\n'
        if "geospatial_lat_min" in props and "geospatial_lat_max" in props
        else ""
    ) + (
        f'| Bounding box longitude | {props["geospatial_lon_min"]} to '
        f'{props["geospatial_lon_max"]} |\n'
        if "geospatial_lon_min" in props and "geospatial_lon_max" in props
        else ""
    ) + (
        f'| Time range | {props["time_coverage_start"]} to {props["time_coverage_end"]} |\n'
        if "time_coverage_start" in props
        else ""
    ) + (
        f'| Time period | {props["time_period"]} |\n' if "time_period" in props else ""
    ) + (
        f'| Contributor | {props["contributor_name"]} |\n'
        if "contributor_name" in props
        else ""
    ) + (
        f'| Creator | {props["creator_name"]} |\n' if "creator_name" in props else ""
    ) + (
        f"\n[Click here for full dataset metadata.](#full-metadata)\n\n"
    )


# def make_variable_list_table(variables: List[Dict[str, Any]]) -> str:
def make_variable_list_table(base_ds: xr.Dataset) -> str:
    """Create a table with brief information about the variables in a dataset

    Args:
        variables: a list of dictionaries of variable properties

    Returns:
        Markdown source for a table summarizing the variables

    """
    lines = ["| Variable | Identifier | Units |", "| ---- | ---- | ---- |"]
    # for variable in variables:
    for variable in base_ds.data_vars:
        long_name = escape_for_markdown(
            base_ds[variable].attrs.get("long_name", "[none]"), False
        )
        name = escape_for_markdown(variable, False)
        units = escape_for_markdown(
            base_ds[variable].attrs.get("units", "[none]"), False
        )
        lines.append(f"| [{long_name}](#{name}) | {name} | {units} |")
    return "\n".join(lines) + "\n\n"


def make_table(data: Dict[str, Any], source_link: str = None) -> str:
    """Create a table showing the entries in a dictionary

    Args:
        data: the data to be displayed
        source_link: if supplied and if a `source` key is present, the
            value for "source" in the table will be replaced with a
            Markdown link to this location.

    Returns:
        Markdown source for a table
    """
    lines = ["| Field | Value |", "| ---- | ---- |"]
    for field, raw_value in data.items():
        value = (
            f"[Click here for source.]({source_link})"
            if field == "source" and source_link is not None
            else f"{escape_for_markdown(raw_value, False)}"
        )
        lines.append(f"| {escape_for_markdown(field, False)} | {value} |")
    return "\n".join(lines) + "\n\n"


def escape_for_markdown(content: Any, as_string: bool = True) -> Any:
    """Turn a string or list into a Markdown source string

    For a string, characters which have special meaning in Markdown will
    be escaped to ensure that they display correctly. Additionally, if the
    string begins with "http://", "https://", or "www." it will be turned into
    a Markdown link.

    For a list, each element will be processed recursively with another call
    to this function, and they will be joined into a single string with ", "
    as separator.

    For any other type, the output is the same as the input.

    Args:
        content: anything

    Returns:
        For strings and lists: Markdown source which will produce a
        representation of the input. For any other type: the input value.
    """
    if type(content) == list:
        return ", ".join(map(escape_for_markdown, content))
    elif type(content) == str:
        escaped_text = re.sub(r"[][({`*_#+.!})\\-]", r"\\\g<0>", content)
        if re.match("https?://", content):
            return f"[{escaped_text}]({content})"
        elif re.match("www[.]", content):
            return f"[{escaped_text}](http://{content})"
        else:
            return escaped_text
    else:
        if as_string:
            return str(content)
        return content


def make_map(props: Dict[str, Any], output_path: str) -> None:
    """Create a bounding box map from a dataset's properties

    The map shows the dataset's bounding box at the centre of a map covering a
    larger area.

    Args:
        props: property dictionary for a dataset
        output_path: the path to which to write the map. The output format
            is determined by the file extension of this path.
    """
    if (
        "geospatial_lon_min" not in props
        or "geospatial_lon_max" not in props
        or "geospatial_lat_min" not in props
        or "geospatial_lat_max" not in props
    ):
        return
    x0 = props["geospatial_lon_min"]
    x1 = props["geospatial_lon_max"]
    y0 = props["geospatial_lat_min"]
    y1 = props["geospatial_lat_max"]
    w = x1 - x0
    h = y1 - y0

    # Above a certain size, we switch from a regional LAEA projection to
    # a global Mollweide projection.
    large = w > 45 or h > 45

    margin_factor = 0.2  # how much margin to include around the bbox
    image_tiles = cartopy.io.img_tiles.OSM()
    plt.figure()
    projection = (
        cartopy.crs.Mollweide(central_longitude=(x0 + x1) / 2)
        if large
        else cartopy.crs.LambertAzimuthalEqualArea(
            (x0 + x1) / 2,
            (y0 + y1) / 2,
            # centre the projection over our bbox
        )
    )
    ax = plt.axes(projection=projection)
    if large:
        ax.set_global()
    else:
        ax.set_extent(
            [
                x0 - margin_factor * w,
                x1 + margin_factor * w,
                y0 - margin_factor * h,
                y1 + margin_factor * h,
            ],
            crs=cartopy.crs.Geodetic(),
        )

    # We use a crude test to choose the tile resolution; ideally we should
    # calculate this more carefully from the bbox size and final image
    # resolution.
    ax.add_image(image_tiles, 3 if large else 6)

    bbox_rect_patch = patches.Rectangle((x0, y0), w, h)
    # Since projected rectangle sides may not be straight, we interpolate
    # them into many short line segments which can be projected separately. In
    # some cases cartopy can do this automatically, but it doesn't seem to work
    # for our projection and parameters (as of cartopy 0.21.0), so we use the
    # manual approach.
    bbox_path_patch = patches.PathPatch(
        bbox_rect_patch.get_path()
        .transformed(bbox_rect_patch.get_patch_transform())
        .interpolated(100),
        linewidth=2,
        edgecolor="red",
        facecolor="none",
        transform=cartopy.crs.Geodetic(),
        zorder=1e6,  # on top
    )
    ax.add_patch(bbox_path_patch)
    ax.gridlines(draw_labels=not large, color="white")
    plt.tight_layout(pad=0)
    plt.savefig(output_path, bbox_inches="tight", pad_inches=0.1)


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) == 2 else os.getcwd()
    keys = ["model-data", "romania", "georgia", "ukraine", "turkey", "blacksea"]
    for key in keys:
        create_doors_dataset_docs(output_dir, key)
