import json

import xarray as xr
import numpy as np

from IPython.display import display


def _display_velocity(data, **kwargs):
    mime_type = 'application/velocity+json'

    bundle = {}
    bundle[mime_type] = json.dumps(data)

    metadata = {}
    metadata[mime_type] = kwargs

    return display(bundle, metadata=metadata, raw=True)


@xr.register_dataset_accessor('xvelmap')
class VelocityMap(object):
    """A xarray.Dataset extension to plot velocity fields on
    tile maps in JupyterLab.

    """
    def __init__(self, ds):
        self._ds = ds

    def plot(self, u_var, v_var, lat_dim='latitude', lon_dim='longitude',
             units=None, **kwargs):
        """Display a velocity field as an interactive map.

        Only works in JupyterLab with the jupyterlab_velocity extension.

        Assumes that the velocity components are given on a regular grid
        (fixed spacing in latitude and longitude).

        Parameters
        ----------
        u_var : str
            Name of the U-component (zonal) variable.
        v_var : str
            Name of the V-component (meridional) variable.
        lat_dim : str, optional
            Name of the latitude dimension/coordinate
            (default: 'latitude').
        lon_dim : str, optional
            Name of the longitude dimension/coordinate
            (default: 'longitude').
        units : str, optional
            Velocity units (default: try getting units from the
            'units' attributes of `u_var` and `v_var`).
        **kwargs : key:value
            Display options for the interactive map.

        """
        ds = self._ds.copy()
        for var_name in (u_var, v_var):
            var_dims = ds[var_name].dims

            if set(var_dims) != set([lat_dim, lon_dim]):
                raise ValueError(
                    "Invalid dimensions for variable '{}' in Dataset: "
                    "should include only {}, found {}."
                    .format(var_name, (lat_dim, lon_dim), var_dims)
                )

            # If dataset contains nans replace with 0
            ds[var_name] = ds[var_name].fillna(0)

        if units is None:
            u_var_units = ds[u_var].attrs.get('units')
            v_var_units = ds[v_var].attrs.get('units')

            if u_var_units != v_var_units:
                raise ValueError(
                    "Different units found for U-component '{}' and "
                    "V-component '{}' variables: '{}' and '{}'"
                    .format(u_var, v_var, u_var_units, v_var_units))

            units = u_var_units

        if units is None:
            units = ''
            
        # Data should be in gaussian grid format (latitudes descending)
        if np.any(np.diff(ds[lat_dim].values) >= 0):
            ds = ds.sel(**{lat_dim: slice(None, None, -1)})

        # infer grid specifications (assume a rectangular grid)
        lat = ds[lat_dim].values
        lon = ds[lon_dim].values

        lon_left = float(lon.min())
        lon_right = float(lon.max())
        lat_lower = float(lat.min())
        lat_upper = float(lat.max())

        dx = float((lon_right - lon_left) / (lon.size - 1))
        dy = float((lat_upper - lat_lower) / (lat.size - 1))

        nx = lon.size
        ny = lat.size

        u_v_spec = ([2, 3],
                    ["Eastward current", "Northward current"],
                    [u_var, v_var])

        velocity_data = []

        for p_number, p_name, var_name in zip(*u_v_spec):
            velocity_data.append({
                "header": {
                    "parameterUnit": units,
                    "parameterNumber": p_number,
                    "dx": dx, "dy": dy,
                    "parameterNumberName": p_name,
                    "la1": lat_upper,
                    "la2": lat_lower,
                    "parameterCategory": 2,
                    "lo2": lon_right,
                    "nx": nx,
                    "ny": ny,
                    "refTime": "2017-02-01 23:00:00",
                    "lo1": lon_left
                    },
                "data": ds[var_name].values.flatten().tolist()
            })

        # map center
        latlon_center = (lat.mean(), lon.mean())

        display_options = {'latlon_center': latlon_center}
        display_options.update(kwargs)

        return _display_velocity(velocity_data, **display_options)
