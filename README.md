# xvelmap

[![Binder with JupyterLab](https://img.shields.io/badge/launch-jupyterlab_on_binder-red.svg)](http://mybinder.org/v2/gh/benbovy/xvelmap/master?urlpath=lab)

A xarray extension to show velocity fields as interactive maps in
jupyterlab.

**Experimental.**

## Dependencies

- Python 3
- [xarray](http://xarray.pydata.org)
- [ipython](https://github.com/ipython/ipython)
- [jupyterlab_velocity](https://github.com/benbovy/jupyterlab_velocity)

## Installation

```
$ conda install -c conda-forge xarray netcdf4 jupyterlab nodejs
$ jupyter labextension install jupyterlab_velocity
$ pip install git+https://github.com/benbovy/xvelmap.git
```
