#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 14:04:48 2020

@author: ziskin
"""
from PW_paths import work_yuval
ionex_path = work_yuval / 'ionex'
# frequencies, Hz for GPS sat system:
F1 = 1575.42 * 1e6
F2 = 1227.60 * 1e6
F5 = 1176.45 * 1e6
speed_of_light = 299792458  # m/s


def stec_to_arcs_epochs_all_sats(stec_ds):
    import xarray as xr
    print('assembeling all sats to arcs and epochs.')
    stec_p4 = stec_ds['tec_p4']
    da_list = []
    for sat_id in stec_p4.sv:
        da_list.append(assemble_epochs_arcs_stec(stec_p4.sel(sv=sat_id)))
    stec = xr.concat(da_list, 'sv')
    stec['sv'] = stec_p4['sv']
    print('Done!')
    return stec


def assemble_epochs_arcs_stec(stec):
    # input is stec['tec_p4'].sel(sv='G01')
    from aux_gps import compute_consecutive_events_datetimes
    import pandas as pd
    stec_events = compute_consecutive_events_datetimes(stec.reset_coords(drop=True))
    stec_no_time = stec_events.to_dataset('event').drop('time')
    series_list = [pd.Series(stec_no_time[x].dropna('time').values) for x in
                   stec_no_time.data_vars]
    da = pd.DataFrame(series_list).T.to_xarray().to_array('arc')
    da = da.rename({'index': 'epoch'})
    da.attrs = stec_events.attrs
    return da


def smooth_p4_one_sat(p4, l4):
    import numpy as np
    import xarray as xr
    # from aux_gps import xr_reindex_with_date_range
    p4_arcs = []
    for arc in p4.event.values:
        time = p4.sel(event=arc).dropna('time')['time']
        p4_arc = p4.sel(event=arc).dropna('time').values
        l4_arc = l4.sel(event=arc).dropna('time').values
        epochs = len(p4_arc)
        if epochs > 0:
            # w = np.ones(p4_arc.shape) / np.arange(1, epochs+1)
            p_sm = np.empty(p4_arc.shape)
            p_sm[0] = p4_arc[0]
            for t in np.arange(1, epochs):
                p4_prd = p_sm[t-1] + l4_arc[t] - l4_arc[t-1]
                w = 1.0 / (t + 1)
                p_sm[t] = w*p4_arc[t] + (1 - w)*p4_prd
            p_sm = xr.DataArray(p_sm, dims=['time'])
            p_sm['time'] = time
            p4_arcs.append(p_sm)
    p4_smoothed_sat = xr.concat(p4_arcs, 'time')
    # p4_smoothed_sat = xr_reindex_with_date_range(p4_smoothed_sat, freq='30S')
    return p4_smoothed_sat


def smooth_all_p4_in_long_term_rinex(rinex_ds, sat='GPS'):
    from aux_gps import compute_consecutive_events_datetimes
    import xarray as xr
    print('smoothing all P4 in rinex dataset...')
    sat_dict = dict(rinex_ds.attrs['satellite system identifier'])
    sat_id = sat_dict.get(sat)
    sat_grp = [x for x in rinex_ds.sv.values if sat_id in x]
    rinex = rinex_ds.sel(sv=sat_grp)
    P4 = rinex['P4'].to_dataset('sv')
    L4 = rinex['L4'].to_dataset('sv')
    p4_list = []
    l4_list = []
    for sat_num in rinex.sv.values:
        p4_list.append(compute_consecutive_events_datetimes(P4[sat_num],
                                                            minimum_epochs=30))
        l4_list.append(compute_consecutive_events_datetimes(L4[sat_num],
                                                            minimum_epochs=30))
    P4 = xr.merge(p4_list)
    P4.attrs['name'] = 'P4'
    L4 = xr.merge(l4_list)
    L4.attrs['name'] = 'L4'
    p4_list = []
    for p4, l4 in zip(P4.data_vars.values(), L4.data_vars.values()):
        p4_smoothed = smooth_p4_one_sat(p4, l4)
        p4_list.append(p4_smoothed)
    P4_smoothed = xr.concat(p4_list, 'sv')
    P4_smoothed['sv'] = rinex.sv
    P4_smoothed.name = 'P4_smoothed'
    P4_smoothed = P4_smoothed.reset_coords(drop=True).sortby('sv')
    print('Done!')
    return P4_smoothed


def read_all_rinex_files_in_path(path=ionex_path):
    import xarray as xr
    from aux_gps import path_glob
    files = path_glob(path, '*.*o')
    rnxs = [read_rinex_obs_with_attrs(x) for x in files]
    rinex_ds = xr.concat(rnxs, 'time')
    rinex_ds = rinex_ds.sortby('time')
    return rinex_ds


def read_all_dcb_files_in_path(path=ionex_path, source='cddis'):
    import xarray as xr
    from aux_gps import path_glob
    import pandas as pd
    if source == 'cddis':
        files = path_glob(path, '*.*i')
        dcb_list = []
        for file in files:
            _, dcb = read_ionex_xr(file, plot=None)
            dcb_list.append(dcb)
    elif source == 'bern':
        files = path_glob(path, '*.DCB')
        dcb_list = [read_code_dcb_xr(x) for x in files]
    dts = [x.attrs['datetime'] for x in dcb_list]
    time = pd.to_datetime(dts)
    dcb_ds = xr.concat(dcb_list, 'time')
    dcb_ds['time'] = time
    dcb_ds = dcb_ds.sortby('time')
    return dcb_ds



# def compute_long_term_stec(rinex_ds, dcb_ds, sat='GPS', station='bshm'):
#     import xarray as xr
#     import pandas as pd
#     daily_stec = []
#     for day in dcb_ds.time.values:
#         day = pd.to_datetime(day).strftime('%Y-%m-%d')
#         rinex_daily = rinex_ds.sel(time=day)
#         dcb_daily = dcb_ds.sel(time=day).reset_coords(drop=True)
#         daily_stec.append(compute_daily_stec(rinex_daily, dcb_daily, sat=sat,
#                                              station=station))
#     stec_ds = xr.concat(daily_stec, 'time')
#     return stec_ds


def compute_stec(rinex_ds, dcb_ds, sat='GPS', station='bshm'):
    """
    Compute slant tec for each sat group and gps station.

    Parameters
    ----------
    rinex_ds : rinex dataset
        DESCRIPTION.
    ionex_dcb: diffrential code biases for stations and satellites, dataset
    sat : TYPE, optional
        DESCRIPTION. The default is 'GPS'.
        'GPS', 'GLONASS', 'SBAS_payload', 'Galileo', 'Compass'
    station : TYPE, optional
        DESCRIPTION. The default is 'bshm'.
    source : TYPE, optional
        DESCRIPTION. The default is 'cddis'.
        'cddis', 'bern'
    Returns
    -------
    rinex : TYPE
        DESCRIPTION.

    """
    import xarray as xr
    # select sat group
    sat_dict = dict(rinex_ds.attrs['satellite system identifier'])
    sat_id = sat_dict.get(sat)
    sat_grp = [x for x in rinex_ds.sv.values if sat_id in x]
    # rinex = rinex_ds.sel(sv=sat_grp)
    # smooth P4:
    P4_smoothed = smooth_all_p4_in_long_term_rinex(rinex_ds, sat='GPS')
    # dcb station in meters:
    dcb_st = dcb_ds.station_bias.sel(station=station) * 1e-9 * speed_of_light
    # dcb sat in meters:
    dcb_sat = dcb_ds.bias * 1e-9 * speed_of_light
    tec_list = []
    for sat in sat_grp:
        try:
            tec = compute_via_p(
                P4_smoothed.sel(sv=sat), F1, F2, dcb_sat.sel(sv=sat), dcb_st)
            tec_list.append(tec)
        except KeyError:
            pass
    stec = xr.Dataset()
    stec['tec_p4'] = xr.concat(tec_list, 'sv')
    # rinex['tec_p1p2'] = compute_via_p(rinex.P1, rinex.P2, F1, F2)
    stec['tec_p4'].attrs['name'] = 'tec from P1 and P2'
    stec['tec_p4'].attrs['unit'] = 'TECU'
    # stec['tec_l1l2'] = compute_via_l(rinex.L1, rinex.L2, F1, F2, speed_of_light)
    # stec['tec_l1l2'].attrs['name'] = 'tec from L1 and L2'
    # stec['tec_l1l2'].attrs['unit'] = 'TECU'
    # stec['tec_l1c1'] = compute_via_l1_c1(rinex.L1, rinex.C1, F1, speed_of_light)
    # stec['tec_l1c1'].attrs['name'] = 'tec from L1 and C1'
    # stec['tec_l1c1'].attrs['unit'] = 'TECU'
    stec.attrs['dcb source'] = dcb_ds.attrs['data source']
    stec.attrs['position'] = rinex_ds.attrs['position']
    stec.attrs['satellite system identifier'] = rinex_ds.attrs['satellite system identifier']
    return stec


def tec_factor(f1, f2):
    """Tec_factor(f1, f2) -> the factor.

    TEC factor to calculate TEC, TECU.

    Parameters
    ----------
    f1 : float
    f2 : float
    Returns
    -------
    factor : float
    """
    return (1 / 40.308) * (f1 ** 2 * f2 ** 2) / (f1 ** 2 - f2 ** 2) * 1.0e-16


def compute_via_p(p4, f1, f2, dcb_sat=None, dcb_station=None):
    import xarray as xr
    """compute_via_p(p4, f1, f2) -> tec.

    calculate a TEC value using pseudorange data.

    Parameters
    ----------
    p4 : float
        f1 pseudorange value - f2 pseudorange value, meters
    f1 : float
        f1 frequency, Hz
    f2 : float
        f2 frequency, Hz
    """
    if dcb_station is None and dcb_sat is None:
        tec = -tec_factor(f1, f2) * (p4)
    else:
        tecs = []
        for time in dcb_sat.time.values:
            dcb_sat_daily = dcb_sat.sel(time=time).values.item()
            dcb_station_daily = dcb_station.sel(time=time).values.item()
            tecs.append(tec_factor(f1, f2) * (p4.sel(time=str(time)[0:10]) + dcb_sat_daily + dcb_station_daily))
        tec = xr.concat(tecs, 'time')
    return tec


def compute_via_l(l1, l2, f1, f2, C, l0=0):
    """compute_via_l(l1, l2, l0, f1, f2) -> tec
    reconstruct a TEC value using phase data.
    Parameters
    ----------
    l1 : float
        f1 phase value, whole cycles
    l2 : float
        f2 phase value, whole cycles
    f1 : float
        f1 frequency, Hz
    f2 : float
        f2 frequency, Hz
    l0 : float
        initial phase, Hz; default = 0
    """

    # c/f = λ
    tec = tec_factor(f1, f2) * (C / f1 * l1 - C / f2 * l2) - l0

    return tec


def compute_via_l1_c1(l1, c1, f1, C):
    """compute_via_l1_c1(l1, c1, f1) -> tec:
    reconstruct a TEC value using pseudorange and phase data (f1).
    Parameters
    ----------
    l1 : float
        f1 phase, whole cycles
    c1 : float
        f1 pseudorange (C/A-code), meters
    f1 : float
        f1 frequency value, Hz
    """

    tec = 0.5 * f1 ** 2 / 40.308 * (c1 - l1 * C / f1) * 1.0e-16

    return tec


def read_rinex_obs_with_attrs(filepath=ionex_path/'bshm0210.20o'):
    import georinex as gr
    import pandas as pd
    from aux_gps import get_timedate_and_station_code_from_rinex
    ds = gr.load(filepath)
    print('reading {} rinex file'.format(filepath.as_posix().split('/')[-1]))
    dt, station = get_timedate_and_station_code_from_rinex(ds.attrs['filename'])
    ds.attrs['starting datetime'] = dt
    ds.attrs['station'] = station
    ssi = {'GPS': 'G', 'GLONASS': 'R', 'SBAS_payload': 'S', 'Galileo': 'E',
           'Compass': 'C'}
    ssi_list = list(ssi.items())
    ds.attrs['satellite system identifier'] = ssi_list
    names = {'P': 'pseudorange value', 'C': 'pseudorange value',
             'L': 'carrier phase value', 'S': 'raw signal strength value'}
    units = {'P': 'm', 'C': 'm', 'L': 'full cycles', 'S': 'dbHz'}
    ds['time'] = pd.to_datetime(ds['time'])
    for da in ds.data_vars.keys():
        ds[da].attrs['name'] = names.get(da[0])
        ds[da].attrs['unit'] = units.get(da[0])
    if 'P1' in ds.data_vars and 'P2' in ds.data_vars:
        ds['P4'] = ds['P2'] - ds['P1']
    if 'L1' in ds.data_vars and 'L2' in ds.data_vars:
        ds['L4'] = ds['L1']*(speed_of_light/F1) - ds['L2']*(speed_of_light/F2)
    return ds


def add_horizontal_colorbar(fg_obj, rect=[0.1, 0.1, 0.8, 0.025], cbar_kwargs_dict=None):
    # rect = [left, bottom, width, height]
    # add option for just figure object, now, accepts facetgrid object only
    cbar_kws = {'label': '', 'format': '%0.2f'}
    if cbar_kwargs_dict is not None:
        cbar_kws.update(cbar_kwargs_dict)
    cbar_ax = fg_obj.fig.add_axes(rect)
    fg_obj.add_colorbar(cax=cbar_ax, orientation="horizontal", **cbar_kws)
    return fg_obj


def get_dt_from_single_ionex(ionex_str):
    import datetime
    import pandas as pd
    code = ionex_str[0:4]
    days = int(ionex_str[4:7])
    year = ionex_str[-3:-1]
    Year = datetime.datetime.strptime(year, '%y').strftime('%Y')
    dt = datetime.datetime(int(Year), 1, 1) + datetime.timedelta(days - 1)
    dt = pd.to_datetime(dt)
    return dt, code


def read_code_dcb_xr(filepath=ionex_path/'COD20021.DCB'):
    import xarray as xr
    import pandas as pd
    print('reading {} DCB file'.format(filepath.as_posix().split('/')[-1]))
    df = pd.read_fwf(filepath, skiprows=6)
    df.columns = ['prn', 'station', 'value', 'rms', 'dt1', 'dt2']
    dt = pd.to_datetime(df.loc[0, 'dt1'], format='%Y %m %d %H %M %S')
    df = df.drop(['dt1', 'dt2'], axis=1)
    station_df = df[~df['station'].isnull()]
    station_split = station_df['station'].str.split(" ", n = 1, expand = True)
    station_df.loc[:, 'station'] = station_split.loc[:, 0].str.lower().values
    # station_df['station_id'] = station_split.loc[:, 1].values
    station_df = pd.pivot_table(station_df, index=['prn', 'station'])
    station_df.columns = ['station_bias_rms', 'station_bias']
    dss = station_df.to_xarray()
    sat_df = df[df['station'].isnull()].drop(['station'], axis=1)
    sat_df.drop(sat_df.tail(1).index, inplace=True) # drop last n rows
    sat_df.columns = ['sv', 'value', 'rms']
    sat_df.set_index(['sv'], inplace=True)
    ds = sat_df.to_xarray()
    ds = ds.rename({'value': 'bias', 'rms': 'bias_rms'})
    ds = xr.merge([ds, dss])
    for da in ds.data_vars.values():
        da.attrs['unit'] = 'ns'
    ds.attrs['name'] = 'DIFFERENTIAL (P1-P2) CODE BIASES FOR SATELLITES AND RECEIVERS'
    ds.attrs['datetime'] = dt.strftime('%Y-%m-%d')
    ds.attrs['data source'] = 'http://ftp.aiub.unibe.ch/BSWUSER52/ORB/'
    return ds


def read_ionex_xr(filepath=ionex_path/'uqrg0210.20i', plot='every_hour',
                  extent=None):
    from getIONEX import read_tec
    import cartopy.crs as ccrs
    import xarray as xr
    import pandas as pd
    print('reading {} ionex file'.format(filepath.as_posix().split('/')[-1]))
    dt, code = get_dt_from_single_ionex(filepath.as_posix().split('/')[-1])
    tecarray, rmsarray, lonarray, latarray, timearray, dcb_list, sta_list = read_tec(
            filepath)
    station = [x[0] for x in sta_list]
    st_bias = xr.DataArray([float(x[1]) for x in sta_list], dims=['station'])
    st_rms = xr.DataArray([float(x[2]) for x in sta_list], dims=['station'])
    bias = xr.DataArray([float(x[1]) for x in dcb_list], dims=['sv'])
    bias_rms = xr.DataArray([float(x[2]) for x in dcb_list], dims=['sv'])
    sv = ['G{}'.format(x[0]) for x in dcb_list]
    tec = xr.DataArray(tecarray, dims=['time', 'lat', 'lon'])
    tec_ds = tec.to_dataset(name='tec') * 10.0
    tec_ds['tec_rms'] = xr.DataArray(rmsarray, dims=['time', 'lat', 'lon']) * 10.0
    tec_ds['tec'].attrs['unit'] = 'TECU'
    tec_ds['tec_rms'].attrs['unit'] = 'TECU'
    tec_ds['lat'] = latarray
    tec_ds['lon'] = lonarray
    time = [pd.Timedelta(x, unit='H') for x in timearray]
    time = [dt + x for x in time]
    tec_ds['time'] = time
    tec_ds = tec_ds.sortby('lat')
    tec_ds.attrs['data source'] = 'ftp://cddis.nasa.gov/gnss/products/ionex/'
    dcb_ds = xr.Dataset()
    dcb_ds['bias'] = bias
    dcb_ds['bias_rms'] = bias_rms
    dcb_ds['sv'] = sv
    dcb_ds['station_bias'] = st_bias
    dcb_ds['station_bias_rms'] = st_rms
    dcb_ds['station'] = station
    dcb_ds.attrs['datetime'] = dt.strftime('%Y-%m-%d')
    dcb_ds.attrs['name'] = 'DIFFERENTIAL (P1-P2) CODE BIASES FOR SATELLITES AND RECEIVERS'
    for da in dcb_ds.data_vars.values():
        da.attrs['unit'] = 'ns'
    dcb_ds = dcb_ds.expand_dims('prn')
    dcb_ds['prn'] = ['G']
    dcb_ds.attrs['data source'] = 'ftp://cddis.nasa.gov/gnss/products/ionex/'
    if plot is not None:
        if plot == 'every_hour':
            times = tec_ds['time'].values[::4][:-1]
            da = tec_ds['tec'].sel(time=times)
            if extent is not None:
                da = da.sel(lon=slice(extent[0], extent[1]), lat=slice(extent[0],extent[1]))
            proj = ccrs.PlateCarree()
            fg = da.plot.contourf(col='time', col_wrap=6,
                                  add_colorbar=False,
                                  cmap='viridis', extend=None, levels=41,
                                  subplot_kws={'projection': proj},
                                  transform=ccrs.PlateCarree(),
                                  figsize=(20, 30))
            fg = add_horizontal_colorbar(fg,
                                         cbar_kwargs_dict={'label': 'TECU'})
            fg.fig.subplots_adjust(top=0.965,
                                   bottom=0.116,
                                   left=0.006,
                                   right=0.985,
                                   hspace=0.0,
                                   wspace=0.046)
        elif isinstance(plot, list):
            time1 = dt + pd.Timedelta(plot[0], unit='H')
            time2 = dt + pd.Timedelta(plot[1], unit='H')
            da = tec_ds['tec'].sel(time=slice(time1, time2))
            if extent is not None:
                da = da.sel(lon=slice(extent[0], extent[1]), lat=slice(extent[0],extent[1]))
            proj = ccrs.PlateCarree()
            fg = da.plot.contourf(col='time', col_wrap=6,
                                  add_colorbar=False,
                                  cmap='viridis', extend=None, levels=41,
                                  subplot_kws={'projection': proj},
                                  transform=ccrs.PlateCarree(),
                                  figsize=(20, 30), robust=True)
            fg = add_horizontal_colorbar(fg,
                                         cbar_kwargs_dict={'label': 'TECU'})
            fg.fig.subplots_adjust(top=0.965,
                                   bottom=0.116,
                                   left=0.006,
                                   right=0.985,
                                   hspace=0.0,
                                   wspace=0.046)

        for i, ax in enumerate(fg.axes.flatten()):
            ax.coastlines(resolution='110m')
            gl = ax.gridlines(crs=ccrs.PlateCarree(),
                              linewidth=1,
                              color='black',
                              alpha=0.5,
                              linestyle='--',
                              draw_labels=False)
            # Without this aspect attributes the maps will look chaotic and the
            # "extent" attribute above will be ignored
    return tec_ds, dcb_ds


    
def read_ionex_file(file):
    import pandas as pd
    df_sat = pd.read_csv(file, skiprows=48, nrows=32,
                         header=None, delim_whitespace=True)
    df_stations = pd.read_fwf(file, skiprows=80, nrows=50, header=None,
                              widths=[20, 10, 10, 10])
    return df_sat, df_stations

def read_one_sinex(file):
    import pandas as pd
    df = pd.read_fwf(file, skiprows=57)
    df.drop(df.tail(2).index, inplace=True) # drop last n rows
    df.columns = ['bias', 'svn', 'prn', 'station', 'obs1', 'obs2',
                  'bias_start', 'bias_end', 'unit', 'value', 'std']
    ds = xr.Dataset()
    ds.attrs['bias'] = df['bias'].values[0]
    df_sat = df[df['station'].isnull()]
    df_station = df[~df['station'].isnull()]
    return ds


def read_sinex(path, glob='*.BSX'):
    from aux_gps import path_glob
    import xarray as xr
    files = path_glob(path, glob_str=glob)
    for file in files:
        ds = read_one_sinex(file)
        ds_list.append(ds)
    dss = xr.concat(ds, 'time')
    return dss