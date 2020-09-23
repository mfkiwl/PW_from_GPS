#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 17:28:04 2020

@author: shlomi
"""
from PW_paths import work_yuval
from matplotlib import rcParams
import seaborn as sns
from pathlib import Path
import matplotlib.pyplot as plt
from PW_paths import savefig_path
import matplotlib.ticker as ticker
tela_results_path = work_yuval / 'GNSS_stations/tela/rinex/30hr/results'
tela_solutions = work_yuval / 'GNSS_stations/tela/gipsyx_solutions'
sound_path = work_yuval / 'sounding'
phys_soundings = sound_path / 'bet_dagan_phys_sounding_2007-2019.nc'
ims_path = work_yuval / 'IMS_T'
gis_path = work_yuval / 'gis'
dem_path = work_yuval / 'AW3D30'
era5_path = work_yuval / 'ERA5'
hydro_path = work_yuval / 'hydro'
ceil_path = work_yuval / 'ceilometers'
aero_path = work_yuval / 'AERONET'


rc = {
    'font.family': 'serif',
    'xtick.labelsize': 'large',
    'ytick.labelsize': 'large'}
for key, val in rc.items():
    rcParams[key] = val
# sns.set(rc=rc, style='white')


def utm_from_lon(lon):
    """
    utm_from_lon - UTM zone for a longitude

    Not right for some polar regions (Norway, Svalbard, Antartica)

    :param float lon: longitude
    :return: UTM zone number
    :rtype: int
    """
    from math import floor
    return floor( ( lon + 180 ) / 6) + 1


def scale_bar(ax, proj, length, location=(0.5, 0.05), linewidth=3,
              units='km', m_per_unit=1000, bounds=None):
    """

    http://stackoverflow.com/a/35705477/1072212
    ax is the axes to draw the scalebar on.
    proj is the projection the axes are in
    location is center of the scalebar in axis coordinates ie. 0.5 is the middle of the plot
    length is the length of the scalebar in km.
    linewidth is the thickness of the scalebar.
    units is the name of the unit
    m_per_unit is the number of meters in a unit
    """
    import cartopy.crs as ccrs
    from matplotlib import patheffects
    # find lat/lon center to find best UTM zone
    try:
        x0, x1, y0, y1 = ax.get_extent(proj.as_geodetic())
    except AttributeError:
        if bounds is not None:
            x0, x1, y0, y1 = bounds
    # Projection in metres
    utm = ccrs.UTM(utm_from_lon((x0+x1)/2))
    # Get the extent of the plotted area in coordinates in metres
    x0, x1, y0, y1 = ax.get_extent(utm)
    # Turn the specified scalebar location into coordinates in metres
    sbcx, sbcy = x0 + (x1 - x0) * location[0], y0 + (y1 - y0) * location[1]
    # Generate the x coordinate for the ends of the scalebar
    bar_xs = [sbcx - length * m_per_unit/2, sbcx + length * m_per_unit/2]
    # buffer for scalebar
    buffer = [patheffects.withStroke(linewidth=5, foreground="w")]
    # Plot the scalebar with buffer
    ax.plot(bar_xs, [sbcy, sbcy], transform=utm, color='k',
        linewidth=linewidth, path_effects=buffer)
    # buffer for text
    buffer = [patheffects.withStroke(linewidth=3, foreground="w")]
    # Plot the scalebar label
    t0 = ax.text(sbcx, sbcy, str(length) + ' ' + units, transform=utm,
        horizontalalignment='center', verticalalignment='bottom',
        path_effects=buffer, zorder=2)
    left = x0+(x1-x0)*0.05
    # Plot the N arrow
    t1 = ax.text(left, sbcy, u'\u25B2\nN', transform=utm,
        horizontalalignment='center', verticalalignment='bottom',
        path_effects=buffer, zorder=2)
    # Plot the scalebar without buffer, in case covered by text buffer
    ax.plot(bar_xs, [sbcy, sbcy], transform=utm, color='k',
        linewidth=linewidth, zorder=3)
    return


@ticker.FuncFormatter
def lon_formatter(x, pos):
    if x < 0:
        return r'{0:.1f}$\degree$W'.format(abs(x))
    elif x > 0:
        return r'{0:.1f}$\degree$E'.format(abs(x))
    elif x == 0:
        return r'0$\degree$'


@ticker.FuncFormatter
def lat_formatter(x, pos):
    if x < 0:
        return r'{0:.1f}$\degree$S'.format(abs(x))
    elif x > 0:
        return r'{0:.1f}$\degree$N'.format(abs(x))
    elif x == 0:
        return r'0$\degree$'


def align_yaxis(ax1, v1, ax2, v2):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    adjust_yaxis(ax2, (y1 - y2) / 2, v2)
    adjust_yaxis(ax1, (y2 - y1) / 2, v1)


def adjust_yaxis(ax, ydif, v):
    """shift axis ax by ydiff, maintaining point v at the same location"""
    inv = ax.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, ydif))
    miny, maxy = ax.get_ylim()
    miny, maxy = miny - v, maxy - v
    if -miny > maxy or (-miny == maxy and dy > 0):
        nminy = miny
        nmaxy = miny * (maxy + dy) / (miny + dy)
    else:
        nmaxy = maxy
        nminy = maxy * (miny + dy) / (maxy + dy)
    ax.set_ylim(nminy + v, nmaxy + v)


def qualitative_cmap(n=2):
    import matplotlib.colors as mcolors
    if n == 2:
        colorsList = [mcolors.BASE_COLORS['r'], mcolors.BASE_COLORS['g']]
        cmap = mcolors.ListedColormap(colorsList)
    elif n == 4:
        colorsList = [
                mcolors.BASE_COLORS['r'],
                mcolors.BASE_COLORS['g'],
                mcolors.BASE_COLORS['c'],
                mcolors.BASE_COLORS['m']]
        cmap = mcolors.ListedColormap(colorsList)
    elif n == 5:
        colorsList = [
                mcolors.BASE_COLORS['r'],
                mcolors.BASE_COLORS['g'],
                mcolors.BASE_COLORS['c'],
                mcolors.BASE_COLORS['m'],
                mcolors.BASE_COLORS['b']]
        cmap = mcolors.ListedColormap(colorsList)
    return cmap


def caption(text, color='blue', **kwargs):
    from termcolor import colored
    print(colored('Caption:', color, attrs=['bold'], **kwargs))
    print(colored(text, color, attrs=['bold'], **kwargs))
    return


def fix_time_axis_ticks(ax, limits=None, margin=15):
    import pandas as pd
    import matplotlib.dates as mdates
    if limits is not None:
        ax.set_xlim(*pd.to_datetime(limits))
    years_fmt = mdates.DateFormatter('%Y')
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(years_fmt)
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
#    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
#    formatter = mdates.ConciseDateFormatter(locator)
#    ax.xaxis.set_major_locator(locator)
#    ax.xaxis.set_major_formatter(formatter)
    return ax


def plot_mean_std_count(da_ts, time_reduce='hour', reduce='mean',
                        count_factor=1):
    import xarray as xr
    import seaborn as sns
    """plot mean, std and count of Xarray dataarray time-series"""
    cmap = sns.color_palette("colorblind", 2)
    time_dim = list(set(da_ts.dims))[0]
    grp = '{}.{}'.format(time_dim, time_reduce)
    if reduce == 'mean':
        mean = da_ts.groupby(grp).mean()
    elif reduce == 'median':
        mean = da_ts.groupby(grp).median()
    std = da_ts.groupby(grp).std()
    mean_plus_std = mean + std
    mean_minus_std = mean - std
    count = da_ts.groupby(grp).count()
    if isinstance(da_ts, xr.Dataset):
        dvars = [x for x in da_ts.data_vars.keys()]
        assert len(dvars) == 2
        secondary_y = dvars[1]
    else:
        secondary_y = None
    fig, axes = plt.subplots(2, 1, sharex=True, sharey=False, figsize=(15, 15))
    mean_df = mean.to_dataframe()
    if secondary_y is not None:
        axes[0] = mean_df[dvars[0]].plot(
            ax=axes[0], linewidth=2.0, marker='o', color=cmap[0])
        ax2mean = mean_df[secondary_y].plot(
            ax=axes[0],
            linewidth=2.0,
            marker='s',
            color=cmap[1],
            secondary_y=True)
        h1, l1 = axes[0].get_legend_handles_labels()
        h2, l2 = axes[0].right_ax.get_legend_handles_labels()
        handles = h1 + h2
        labels = l1 + l2
        axes[0].legend(handles, labels)
        axes[0].fill_between(mean_df.index.values,
                             mean_minus_std[dvars[0]].values,
                             mean_plus_std[dvars[0]].values,
                             color=cmap[0],
                             alpha=0.5)
        ax2mean.fill_between(
            mean_df.index.values,
            mean_minus_std[secondary_y].values,
            mean_plus_std[secondary_y].values,
            color=cmap[1],
            alpha=0.5)
        ax2mean.tick_params(axis='y', colors=cmap[1])
    else:
        mean_df.plot(ax=axes[0], linewidth=2.0, marker='o', color=cmap[0])
        axes[0].fill_between(
            mean_df.index.values,
            mean_minus_std.values,
            mean_plus_std.values,
            color=cmap[0],
            alpha=0.5)
    axes[0].grid()
    count_df = count.to_dataframe() / count_factor
    count_df.plot.bar(ax=axes[1], rot=0)
    axes[0].xaxis.set_tick_params(labelbottom=True)
    axes[0].tick_params(axis='y', colors=cmap[0])
    fig.tight_layout()
    if secondary_y is not None:
        return axes, ax2mean
    else:
        return axes


def plot_seasonal_histogram(da, dim='sound_time', xlim=None, xlabel=None,
                            suptitle=''):
    fig_hist, axs = plt.subplots(2, 2, sharex=False, sharey=True,
                                 figsize=(10, 8))
    seasons = ['DJF', 'MAM', 'JJA', 'SON']
    cmap = sns.color_palette("colorblind", 4)
    for i, ax in enumerate(axs.flatten()):
        da_season = da.sel({dim: da['{}.season'.format(dim)] == seasons[i]}).dropna(dim)
        ax = sns.distplot(da_season, ax=ax, norm_hist=False,
                          color=cmap[i], hist_kws={'edgecolor': 'k'},
                          axlabel=xlabel,
                          label=seasons[i])
        ax.set_xlim(xlim)
        ax.legend()
    #            axes.set_xlabel('MLH [m]')
        ax.set_ylabel('Frequency')
    fig_hist.suptitle(suptitle)
    fig_hist.tight_layout()
    return axs


def plot_two_histograms_comparison(x, y, bins=None, labels=['x', 'y'],
                                   ax=None, colors=['b', 'r']):
    import numpy as np
    import matplotlib.pyplot as plt
    x_w = np.empty(x.shape)
    x_w.fill(1/x.shape[0])
    y_w = np.empty(y.shape)
    y_w.fill(1/y.shape[0])
    if ax is None:
        fig, ax = plt.subplots()
    ax.hist([x, y], bins=bins, weights=[x_w, y_w], color=colors,
            label=labels)
    ax.legend()
    return ax

def plot_diurnal_wind_hodograph(path=ims_path, station='TEL-AVIV-COAST',
                                season=None, cmax=None, ax=None):
    import xarray as xr
    from metpy.plots import Hodograph
    # import matplotlib
    import numpy as np
    colorbar=False
    # from_list = matplotlib.colors.LinearSegmentedColormap.from_list
    cmap = plt.cm.get_cmap('hsv', 24)
    # cmap = from_list(None, plt.cm.jet(range(0,24)), 24)
    U = xr.open_dataset(path / 'IMS_U_israeli_10mins.nc')
    V = xr.open_dataset(path / 'IMS_V_israeli_10mins.nc')
    u_sta = U[station]
    v_sta = V[station]
    u_sta.load()
    v_sta.load()
    if season is not None:
        print('{} season selected'.format(season))
        u_sta = u_sta.sel(time=u_sta['time.season'] == season)
        v_sta = v_sta.sel(time=v_sta['time.season'] == season)
    u = u_sta.groupby('time.hour').mean()
    v = v_sta.groupby('time.hour').mean()
    if ax is None:
        colorbar = True
        fig, ax = plt.subplots()
    max_uv = max(max(u.values), max(v.values)) + 1
    if cmax is None:
        max_uv = max(max(u.values), max(v.values)) + 1
    else:
        max_uv = cmax
    h = Hodograph(component_range=max_uv, ax=ax)
    h.add_grid(increment=0.5)
    # hours = np.arange(0, 25)
    lc = h.plot_colormapped(u, v, u.hour,cmap=cmap, linestyle='-', linewidth=2)
    #ticks = np.arange(np.min(hours), np.max(hours))
    # cb = fig.colorbar(lc, ticks=range(0,24), label='Time of Day [UTC]')
    if colorbar:
        cb = ax.figure.colorbar(lc, ticks=range(0,24), label='Time of Day [UTC]')
    # cb.ax.tick_params(length=0)
    if season is None:
        ax.figure.suptitle('{} diurnal wind Hodograph'.format(station))
    else:
        ax.figure.suptitle('{} diurnal wind Hodograph {}'.format(station, season))
    ax.set_xlabel('North')
    ax.set_ylabel('East')
    ax.set_title('South')
    ax2 = ax.twinx()
    ax2.tick_params(axis='y', right=False, labelright=False)
    ax2.set_ylabel('West')
    # axcb = fig.colorbar(lc)
    return ax


def plot_MLR_GNSS_PW_harmonics_facetgrid(path=work_yuval, season='JJA',
                                         n_max=2, ylim=None, save=True):
    import xarray as xr
    from aux_gps import run_MLR_diurnal_harmonics
    from matplotlib.ticker import AutoMinorLocator
    import numpy as np
    harmonics = xr.load_dataset(path / 'GNSS_PW_harmonics_diurnal.nc')
#    sites = sorted(list(set([x.split('_')[0] for x in harmonics])))
#    da = xr.DataArray([x for x in range(len(sites))], dims='GNSS')
#    da['GNSS'] = sites
    sites = group_sites_to_xarray(upper=False, scope='diurnal')
    sites_flat = [x for x in sites.values.flatten()]
    da = xr.DataArray([x for x in range(len(sites_flat))], dims='GNSS')
    da['GNSS'] = [x for x in range(len(da))]
    fg = xr.plot.FacetGrid(
        da,
        col='GNSS',
        col_wrap=3,
        sharex=False,
        sharey=False, figsize=(20, 20))
    
    for i in range(fg.axes.shape[0]):  # i is rows
        for j in range(fg.axes.shape[1]):  # j is cols
            site = sites.values[i, j]
            ax = fg.axes[i, j]
            try:
                harm_site = harmonics[[x for x in harmonics if site in x]]
                if site in ['nrif']:
                    leg_loc = 'upper center'
                elif site in ['yrcm', 'ramo']:
                    leg_loc = 'lower center'
#                elif site in ['katz']:
#                    leg_loc = 'upper right'
                else:
                    leg_loc = None
                ax = run_MLR_diurnal_harmonics(harm_site, season=season,
                                               n_max=n_max, plot=True, ax=ax,
                                               legend_loc=leg_loc, ncol=2,
                                               legsize=16)
                ax.set_xlabel('Hour of day [UTC]', fontsize=16)
                if ylim is not None:
                    ax.set_ylim(*ylim)
                ax.tick_params(axis='x', which='major', labelsize=18)
                ax.yaxis.set_major_locator(plt.MaxNLocator(4))
                ax.yaxis.set_minor_locator(AutoMinorLocator(2))
                ax.tick_params(axis='y', which='major', labelsize=18)
                ax.yaxis.tick_left()
                ax.xaxis.set_ticks(np.arange(0, 23, 3))
                ax.grid()
                ax.set_title('')
                ax.set_ylabel('')
                ax.grid(axis='y', which='minor', linestyle='--')
                ax.text(0.1, .85, site.upper(),
                        horizontalalignment='center', fontweight='bold',
                        transform=ax.transAxes, fontsize=20)
                if j == 0:
                    ax.set_ylabel('PWV anomalies [mm]', fontsize=16)
#                if j == 0:
#                    ax.set_ylabel('PW anomalies [mm]', fontsize=12)
#                elif j == 1:
#                    if i>5:
#                        ax.set_ylabel('PW anomalies [mm]', fontsize=12)
            except TypeError:
                ax.set_axis_off()
                
#    for i, (site, ax) in enumerate(zip(da['GNSS'].values, fg.axes.flatten())):
#        harm_site = harmonics[[x for x in harmonics if sites[i] in x]]
#        if site in ['elat', 'nrif']:
#            loc = 'upper center'
#            text = 0.1
#        elif site in ['elro', 'yrcm', 'ramo', 'slom', 'jslm']:
#            loc = 'upper right'
#            text = 0.1
#        else:
#            loc = None
#            text = 0.1
#        ax = run_MLR_diurnal_harmonics(harm_site, season=season, n_max=n_max, plot=True, ax=ax, legend_loc=loc)
#        ax.set_title('')
#        ax.set_ylabel('PW anomalies [mm]')
#        if ylim is not None:
#            ax.set_ylim(ylim[0], ylim[1])
#        ax.text(text, .85, site.upper(),
#                horizontalalignment='center', fontweight='bold',
#                transform=ax.transAxes)
#    for i, ax in enumerate(fg.axes.flatten()):
#        if i > (da.GNSS.telasize-1):
#            ax.set_axis_off()
#            pass
    fg.fig.subplots_adjust(
        top=0.993,
        bottom=0.032,
        left=0.054,
        right=0.995,
        hspace=0.15,
        wspace=0.12)
    if save:
        filename = 'pw_diurnal_harmonics_{}_{}.png'.format(n_max, season)
#        plt.savefig(savefig_path / filename, bbox_inches='tight')
        plt.savefig(savefig_path / filename, orientation='landscape')
    return fg


def plot_gustiness(path=work_yuval, ims_path=ims_path, site='tela',
                   ims_site='HAIFA-TECHNION', season='JJA', month=None, pts=7,
                   ax=None):
    import xarray as xr
    import numpy as np
    g = xr.open_dataset(ims_path / 'IMS_G{}_israeli_10mins_daily_anoms.nc'.format(pts))[ims_site]
    g.load()
    if season is not None:
        g = g.sel(time=g['time.season'] == season)
        label = 'Gustiness {} IMS station in {} season'.format(
            site, season)
    elif month is not None:
        g = g.sel(time=g['time.month'] == month)
        label = 'Gustiness {} IMS station in {} month'.format(
            site, month)
    elif season is not None and month is not None:
        raise('pls pick either season or month...')
#    date = groupby_date_xr(g)
#    # g_anoms = g.groupby('time.month') - g.groupby('time.month').mean('time')
#    g_anoms = g.groupby(date) - g.groupby(date).mean('time')
#    g_anoms = g_anoms.reset_coords(drop=True)
    G = g.groupby('time.hour').mean('time') * 100.0
    if ax is None:
        fig, ax = plt.subplots(figsize=(16, 8))
    Gline = G.plot(ax=ax, color='b', marker='o', label='Gustiness')
    ax.set_title(label)
    ax.axhline(0, color='b', linestyle='--')
    ax.set_ylabel('Gustiness anomalies [dimensionless]', color='b')
    ax.set_xlabel('Time of day [UTC]')
    # ax.set_xticks(np.arange(0, 24, step=1))
    ax.yaxis.label.set_color('b')
    ax.tick_params(axis='y', colors='b')
    ax.xaxis.set_ticks(np.arange(0, 23, 3))
    ax.grid()
    pw = xr.open_dataset(
        work_yuval /
        'GNSS_PW_hourly_anoms_thresh_50_homogenized.nc')[site]
    pw.load().dropna('time')
    if season is not None:
        pw = pw.sel(time=pw['time.season'] == season)
    elif month is not None:
        pw = pw.sel(time=pw['time.month'] == month)
#    date = groupby_date_xr(pw)
#    pw = pw.groupby(date) - pw.groupby(date).mean('time')
#    pw = pw.reset_coords(drop=True)
    pw = pw.groupby('time.hour').mean()
    axpw = ax.twinx()
    PWline = pw.plot.line(ax=axpw, color='tab:green', marker='s', label='PW ({})'.format(season))
    axpw.axhline(0, color='k', linestyle='--')
    lns = Gline + PWline
    axpw.set_ylabel('PW anomalies [mm]')
    align_yaxis(ax, 0, axpw, 0)
    return lns


def plot_gustiness_facetgrid(path=work_yuval, ims_path=ims_path,
                             season='JJA', month=None, save=True):
    import xarray as xr
    gnss_ims_dict = {
        'alon': 'ASHQELON-PORT', 'bshm': 'HAIFA-TECHNION', 'csar': 'HADERA-PORT',
        'tela': 'TEL-AVIV-COAST', 'slom': 'BESOR-FARM', 'kabr': 'SHAVE-ZIYYON',
        'nzrt': 'DEIR-HANNA', 'katz': 'GAMLA', 'elro': 'MEROM-GOLAN-PICMAN',
        'mrav': 'MAALE-GILBOA', 'yosh': 'ARIEL', 'jslm': 'JERUSALEM-GIVAT-RAM',
        'drag': 'METZOKE-DRAGOT', 'dsea': 'SEDOM', 'ramo': 'MIZPE-RAMON-20120927',
        'nrif': 'NEOT-SMADAR', 'elat': 'ELAT', 'klhv': 'SHANI',
        'yrcm': 'ZOMET-HANEGEV'}
    da = xr.DataArray([x for x in gnss_ims_dict.values()], dims=['GNSS'])
    da['GNSS'] = [x for x in gnss_ims_dict.keys()]
    to_remove = ['kabr', 'nzrt', 'katz', 'elro', 'klhv', 'yrcm', 'slom']
    sites = [x for x in da['GNSS'].values if x not in to_remove]
    da = da.sel(GNSS=sites)
    gnss_order=['bshm', 'mrav', 'drag', 'csar', 'yosh', 'dsea', 'tela', 'jslm',
                'nrif', 'alon', 'ramo', 'elat']
    df = da.to_dataframe('gnss')
    da = df.reindex(gnss_order).to_xarray()['gnss']
    fg = xr.plot.FacetGrid(
        da,
        col='GNSS',
        col_wrap=3,
        sharex=False,
        sharey=False, figsize=(20, 20))
    for i, (site, ax) in enumerate(zip(da['GNSS'].values, fg.axes.flatten())):
        lns = plot_gustiness(path=path, ims_path=ims_path,
                             ims_site=gnss_ims_dict[site],
                             site=site, season=season, month=month, ax=ax)
        labs = [l.get_label() for l in lns]
        if site in ['tela', 'alon', 'dsea', 'csar', 'elat', 'nrif']:
            ax.legend(lns, labs, loc='upper center',prop={'size':8}, framealpha=0.5, fancybox=True, title=site.upper())
        elif site in ['drag']:
            ax.legend(lns, labs, loc='upper right',prop={'size':8}, framealpha=0.5, fancybox=True, title=site.upper())
        else:
            ax.legend(lns, labs, loc='best',prop={'size':8}, framealpha=0.5, fancybox=True, title=site.upper())
        ax.set_title('')
        ax.set_ylabel(r'G anomalies $\times$$10^{2}$')
#        ax.text(.8, .85, site.upper(),
#            horizontalalignment='center', fontweight='bold',
#            transform=ax.transAxes)
    for i, ax in enumerate(fg.axes.flatten()):
        if i > (da.GNSS.size-1):
            ax.set_axis_off()
            pass
    fg.fig.tight_layout()
    fg.fig.subplots_adjust(top=0.974,
                           bottom=0.053,
                           left=0.041,
                           right=0.955,
                           hspace=0.15,
                           wspace=0.3)
    filename = 'gustiness_israeli_gnss_pw_diurnal_{}.png'.format(season)
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_fft_diurnal(path=work_yuval, save=True):
    import xarray as xr
    import numpy as np
    import matplotlib.ticker as tck
    sns.set_style("whitegrid",
                  {'axes.grid': True,
                   'xtick.bottom': True,
                   'font.family': 'serif',
                   'ytick.left': True})
    sns.set_context('paper')
    power = xr.load_dataset(path / 'GNSS_PW_power_spectrum_diurnal.nc')
    power = power.to_array('site')
    sites = [x for x in power.site.values]
    fg = power.plot.line(col='site', col_wrap=4, sharex=False, figsize=(20,18))
    fg.set_xlabels('Frequency [cpd]')
    fg.set_ylabels('PW PSD [dB]')
    ticklabels = np.arange(0, 7)
    for ax, site in zip(fg.axes.flatten(), sites):
        sns.despine()
        ax.set_title('')
        ax.set_xticklabels(ticklabels)
        # ax.tick_params(axis='y', which='minor')
        ax.yaxis.set_minor_locator(tck.AutoMinorLocator())
        ax.set_xlim(0, 6.5)
        ax.set_ylim(70, 125)
        ax.grid(True)
        ax.grid(which='minor', axis='y')
        ax.text(.8, .85, site.upper(),
                horizontalalignment='center', fontweight='bold',
                transform=ax.transAxes)
    fg.fig.tight_layout()
    filename = 'power_pw_diurnal.png'
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_rinex_availability_with_map(path=work_yuval, gis_path=gis_path,
                                     scope='diurnal',
                                     dem_path=dem_path, save=True):
    # TODO: add box around merged stations and removed stations
    # TODO: add color map labels to stations removed and merged
    from aux_gps import gantt_chart
    import xarray as xr
    import pandas as pd
    import geopandas as gpd
    from PW_stations import produce_geo_gnss_solved_stations
    from aux_gps import geo_annotate
    from ims_procedures import produce_geo_ims
    from matplotlib.colors import ListedColormap
    from aux_gps import path_glob
    print('{} scope selected.'.format(scope))
    fig = plt.figure(figsize=(20, 10))
    grid = plt.GridSpec(1, 2, width_ratios=[
        5, 2], wspace=0.1)
    ax_gantt = fig.add_subplot(grid[0, 0])  # plt.subplot(221)
    ax_map = fig.add_subplot(grid[0, 1])  # plt.subplot(122)
#    fig, ax = plt.subplots(1, 2, sharex=False, sharey=False, figsize=(20, 6))
    # RINEX gantt chart:
    if scope == 'diurnal':
        file = path_glob(path, 'GNSS_PW_thresh_50_for_diurnal_analysis.nc')[-1]
    elif scope == 'longterm':
        file = path_glob(path, 'GNSS_PW_thresh_50_homogenized.nc')[-1]
    ds = xr.open_dataset(file)
    just_pw = [x for x in ds if 'error' not in x]
    ds = ds[just_pw]
    da = ds.to_array('station')
    da['station'] = [x.upper() for x in da.station.values]
    ds = da.to_dataset('station')
    title = 'Daily RINEX files availability for the Israeli GNSS stations'
    ax_gantt = gantt_chart(
        ds,
        ax=ax_gantt,
        fw='normal',
        title='',
        pe_dict=None, fontsize=16)
    # Israel gps ims map:
    ax_map = plot_israel_map(gis_path=gis_path, ax=ax_map, ticklabelsize=16)
    # overlay with dem data:
    cmap = plt.get_cmap('terrain', 41)
    dem = xr.open_dataarray(dem_path / 'israel_dem_250_500.nc')
    # dem = xr.open_dataarray(dem_path / 'israel_dem_500_1000.nc')
    fg = dem.plot.imshow(ax=ax_map, alpha=0.5, cmap=cmap,
                         vmin=dem.min(), vmax=dem.max(), add_colorbar=False)
#    scale_bar(ax_map, 50)
    cbar_kwargs = {'fraction': 0.1, 'aspect': 50, 'pad': 0.03}
    cb = plt.colorbar(fg, **cbar_kwargs)
    cb.set_label(label='meters above sea level', size=14, weight='normal')
    cb.ax.tick_params(labelsize=14)
    ax_map.set_xlabel('')
    ax_map.set_ylabel('')
    gps = produce_geo_gnss_solved_stations(path=gis_path, plot=False)
    # removed = ['hrmn', 'nizn', 'spir']
#    removed = ['hrmn']
    if scope == 'diurnal':
        removed = ['hrmn', 'gilb', 'lhav']
    elif scope == 'longterm':
        removed = ['hrmn', 'gilb', 'lhav', 'nizn', 'spir']
    print('removing {} stations from map.'.format(removed))
#    merged = ['klhv', 'lhav', 'mrav', 'gilb']
    merged = []
    gps_list = [x for x in gps.index if x not in merged and x not in removed]
    gps.loc[gps_list, :].plot(ax=ax_map, edgecolor='black', marker='s',
             alpha=1.0, markersize=35, facecolor="None", linewidth=2, zorder=3)
#    gps.loc[removed, :].plot(ax=ax_map, color='black', edgecolor='black', marker='s',
#            alpha=1.0, markersize=25, facecolor='white')
#    gps.loc[merged, :].plot(ax=ax_map, color='black', edgecolor='r', marker='s',
#            alpha=0.7, markersize=25)
    gps_stations = gps_list  # [x for x in gps.index]
#    to_plot_offset = ['mrav', 'klhv', 'nzrt', 'katz', 'elro']
    to_plot_offset = []


    for x, y, label in zip(gps.loc[gps_stations, :].lon, gps.loc[gps_stations,
                                                                 :].lat, gps.loc[gps_stations, :].index.str.upper()):
        if label.lower() in to_plot_offset:
            ax_map.annotate(label, xy=(x, y), xytext=(4, -6),
                            textcoords="offset points", color='k',
                            fontweight='bold', fontsize=12)
        else:
            ax_map.annotate(label, xy=(x, y), xytext=(3, 3),
                            textcoords="offset points", color='k',
                            fontweight='bold', fontsize=12)
#    geo_annotate(ax_map, gps_normal_anno.lon, gps_normal_anno.lat,
#                 gps_normal_anno.index.str.upper(), xytext=(3, 3), fmt=None,
#                 c='k', fw='normal', fs=10, colorupdown=False)
#    geo_annotate(ax_map, gps_offset_anno.lon, gps_offset_anno.lat,
#                 gps_offset_anno.index.str.upper(), xytext=(4, -6), fmt=None,
#                 c='k', fw='normal', fs=10, colorupdown=False)
    # plot bet-dagan:
    df = pd.Series([32.00, 34.81]).to_frame().T
    df.index = ['Bet-Dagan']
    df.columns = ['lat', 'lon']
    bet_dagan = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon,
                                                                 df.lat),
                                 crs=gps.crs)
    bet_dagan.plot(ax=ax_map, color='black', edgecolor='black',
                   marker='x', linewidth=2, zorder=2)
    geo_annotate(ax_map, bet_dagan.lon, bet_dagan.lat,
                 bet_dagan.index, xytext=(4, -6), fmt=None,
                 c='k', fw='bold', fs=12, colorupdown=False)
#    plt.legend(['GNSS \nreceiver sites',
#                'removed \nGNSS sites',
#                'merged \nGNSS sites',
#                'radiosonde\nstation'],
#               loc='upper left', framealpha=0.7, fancybox=True,
#               handletextpad=0.2, handlelength=1.5)
    print('getting IMS temperature stations metadata...')
    ims = produce_geo_ims(path=gis_path, freq='10mins', plot=False)
    ims.plot(ax=ax_map, marker='o', edgecolor='tab:orange', alpha=0.65,
             markersize=15, facecolor="tab:orange", zorder=1)
    # ims, gps = produce_geo_df(gis_path=gis_path, plot=False)
    print('getting solved GNSS israeli stations metadata...')
    plt.legend(['GNSS \nstations',
                'radiosonde\nstation', 'IMS stations'],
           loc='upper left', framealpha=0.7, fancybox=True,
           handletextpad=0.2, handlelength=1.5, fontsize=12)
    fig.subplots_adjust(top=0.95,
                        bottom=0.11,
                        left=0.05,
                        right=0.95,
                        hspace=0.2,
                        wspace=0.2)
    # plt.legend(['IMS stations', 'GNSS stations'], loc='upper left')

    filename = 'rinex_israeli_gnss_map.png'
    caption('Daily RINEX files availability for the Israeli GNSS station network at the SOPAC/GARNER website')
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fig


def plot_means_box_plots(path=work_yuval, thresh=50, kind='box',
                         x='month', col_wrap=5, ylimits=None, twin=None,
                         twin_attrs=None,
                         xlimits=None, anoms=True, bins=None,
                         season=None, attrs_plot=True, save=True, ds_input=None):
    import xarray as xr
    pw = xr.open_dataset(
                work_yuval /
                'GNSS_PW_thresh_{:.0f}_homogenized.nc'.format(thresh))
    pw = pw[[x for x in pw.data_vars if '_error' not in x]]
    attrs = [x.attrs for x in pw.data_vars.values()]
    if x == 'month':
        pw = xr.load_dataset(
                work_yuval /
                'GNSS_PW_monthly_thresh_{:.0f}_homogenized.nc'.format(thresh))
        # pw = pw.resample(time='MS').mean('time')
    elif x == 'hour':
        # pw = pw.resample(time='1H').mean('time')
        # pw = pw.groupby('time.hour').mean('time')
        pw = xr.load_dataset(work_yuval / 'GNSS_PW_hourly_thresh_{:.0f}_homogenized.nc'.format(thresh))
        pw = pw[[x for x in pw.data_vars if '_error' not in x]]
        # first remove long term monthly means:
        if anoms:
            pw = xr.load_dataset(work_yuval / 'GNSS_PW_hourly_anoms_thresh_{:.0f}_homogenized.nc'.format(thresh))
            if twin is not None:
                twin = twin.groupby('time.month') - twin.groupby('time.month').mean('time')
                twin = twin.reset_coords(drop=True)
            # pw = pw.groupby('time.month') - pw.groupby('time.month').mean('time')
    elif x == 'day':
        # pw = pw.resample(time='1H').mean('time')
        # pw = pw.groupby('time.hour').mean('time')
        pw = xr.load_dataset(work_yuval / 'GNSS_PW_daily_thresh_{:.0f}_homogenized.nc'.format(thresh))
        pw = pw[[x for x in pw.data_vars if '_error' not in x]]
        # first remove long term monthly means:
        if anoms:
            # pw = pw.groupby('time.month') - pw.groupby('time.month').mean('time')
            pw = pw.groupby('time.dayofyear') - pw.groupby('time.dayodyear').mean('time')
    if season is not None:
        if season != 'all':
            print('{} season is selected'.format(season))
            pw = pw.sel(time=pw['time.season'] == season)
            all_seas = False
            if twin is not None:
                twin = twin.sel(time=twin['time.season'] == season)
        else:
            print('all seasons selected')
            all_seas = True
    else:
        all_seas = False
    for i, da in enumerate(pw.data_vars):
        pw[da].attrs = attrs[i]
    if not attrs_plot:
        attrs = None
    if ds_input is not None:
        # be carful!:
        pw = ds_input
    fg = plot_multi_box_xr(pw, kind=kind, x=x, col_wrap=col_wrap,
                           ylimits=ylimits, xlimits=xlimits, attrs=attrs,
                           bins=bins, all_seasons=all_seas, twin=twin,
                           twin_attrs=twin_attrs)
    attrs = [x.attrs for x in pw.data_vars.values()]
    for i, ax in enumerate(fg.axes.flatten()):
        try:
            mean_years = float(attrs[i]['mean_years'])
#            print(i)
            # print(mean_years)
        except IndexError:
            ax.set_axis_off()
            pass
    if kind != 'hist':
        [fg.axes[x, 0].set_ylabel('PW [mm]') for x in range(len(fg.axes[:, 0]))]
#    [fg.axes[-1, x].set_xlabel('month') for x in range(len(fg.axes[-1, :]))]
    fg.fig.subplots_adjust(top=0.98,
                           bottom=0.05,
                           left=0.025,
                           right=0.985,
                           hspace=0.27,
                           wspace=0.215)
    if season is not None:
        filename = 'pw_{}ly_means_{}_seas_{}.png'.format(x, kind, season)
    else:
        filename = 'pw_{}ly_means_{}.png'.format(x, kind)
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_annual_pw(path=work_yuval, fontsize=20, labelsize=18,
                   ylim=[7.5, 40], save=True, kind='violin', bins=None):
    """kind can be violin or hist, for violin choose ylim=7.5,40 and for hist
    choose ylim=0,0.3"""
    import xarray as xr
    from synoptic_procedures import slice_xr_with_synoptic_class
    gnss_filename = 'GNSS_PW_monthly_thresh_50_homogenized.nc'
    pw = xr.load_dataset(path / gnss_filename)
    df_annual = pw.to_dataframe()
    fg = plot_pw_geographical_segments(
        df_annual, scope='annual',
        kind=kind,
        fg=None,
        ylim=ylim,
        fontsize=fontsize,
        labelsize=labelsize,
        save=False, bins=bins)
    fg.fig.subplots_adjust(
            top=0.973,
            bottom=0.029,
            left=0.054,
            right=0.995,
            hspace=0.15,
            wspace=0.12)
    if save:
        filename = 'pw_annual_means_{}.png'.format(kind)
        plt.savefig(savefig_path / filename, orientation='portrait')
    return fg


def plot_multi_box_xr(pw, kind='violin', x='month', sharex=False, sharey=False,
                      col_wrap=5, ylimits=None, xlimits=None, attrs=None,
                      bins=None, all_seasons=False, twin=None, twin_attrs=None):
    import xarray as xr
    pw = pw.to_array('station')
    if twin is not None:
        twin = twin.to_array('station')
    fg = xr.plot.FacetGrid(pw, col='station', col_wrap=col_wrap, sharex=sharex,
                           sharey=sharey)
    for i, (sta, ax) in enumerate(zip(pw['station'].values, fg.axes.flatten())):
        pw_sta = pw.sel(station=sta).reset_coords(drop=True)
        if all_seasons:
            pw_seas = pw_sta.sel(time=pw_sta['time.season']=='DJF')
            df = pw_seas.to_dataframe(sta)
            plot_box_df(df, ax=ax, x=x, title=sta, ylabel='', kind=kind,
                        ylimits=ylimits, xlimits=xlimits, attrs=None, bins=bins,
                        marker='o')
            pw_seas = pw_sta.sel(time=pw_sta['time.season']=='MAM')
            df = pw_seas.to_dataframe(sta)
            plot_box_df(df, ax=ax, x=x, title=sta, ylabel='', kind=kind,
                        ylimits=ylimits, xlimits=xlimits, attrs=None, bins=bins,
                        marker='^')
            pw_seas = pw_sta.sel(time=pw_sta['time.season']=='JJA')
            df = pw_seas.to_dataframe(sta)
            plot_box_df(df, ax=ax, x=x, title=sta, ylabel='', kind=kind,
                        ylimits=ylimits, xlimits=xlimits, attrs=None, bins=bins,
                        marker='s')
            pw_seas = pw_sta.sel(time=pw_sta['time.season']=='SON')
            df = pw_seas.to_dataframe(sta)
            plot_box_df(df, ax=ax, x=x, title=sta, ylabel='', kind=kind,
                        ylimits=ylimits, xlimits=xlimits, attrs=attrs[i], bins=bins,
                        marker='x')
            df = pw_sta.to_dataframe(sta)
            plot_box_df(df, ax=ax, x=x, title=sta, ylabel='', kind=kind,
                        ylimits=ylimits, xlimits=xlimits, attrs=attrs[i], bins=bins,
                        marker='d')
            if sta == 'nrif' or sta == 'elat':
                ax.legend(['DJF', 'MAM', 'JJA', 'SON', 'Annual'],
                          prop={'size':8}, loc='upper center', framealpha=0.5, fancybox=True)
            elif sta == 'yrcm' or sta == 'ramo':
                ax.legend(['DJF', 'MAM', 'JJA', 'SON', 'Annual'],
                          prop={'size':8}, loc='upper right', framealpha=0.5, fancybox=True)
            else:
                ax.legend(['DJF', 'MAM', 'JJA', 'SON', 'Annual'],
                          prop={'size':8}, loc='best', framealpha=0.5, fancybox=True)
        else:
        # if x == 'hour':
        #     # remove seasonal signal:
        #     pw_sta = pw_sta.groupby('time.dayofyear') - pw_sta.groupby('time.dayofyear').mean('time')
        # elif x == 'month':
        #     # remove daily signal:
        #     pw_sta = pw_sta.groupby('time.hour') - pw_sta.groupby('time.hour').mean('time')            
            df = pw_sta.to_dataframe(sta)
            if twin is not None:
                twin_sta = twin.sel(station=sta).reset_coords(drop=True)
                twin_df = twin_sta.to_dataframe(sta)
            else:
                twin_df = None
            if attrs is not None:
                plot_box_df(df, ax=ax, x=x, title=sta, ylabel='', kind=kind,
                            ylimits=ylimits, xlimits=xlimits, attrs=attrs[i],
                            bins=bins, twin_df=twin_df, twin_attrs=twin_attrs)
            else:
                plot_box_df(df, ax=ax, x=x, title=sta, ylabel='', kind=kind,
                            ylimits=ylimits, xlimits=xlimits, attrs=None,
                            bins=bins, twin_df=twin_df, twin_attrs=twin_attrs)
    return fg


def plot_box_df(df, x='month', title='TELA', marker='o',
                ylabel=r'IWV [kg$\cdot$m$^{-2}$]', ax=None, kind='violin',
                ylimits=(5, 40), xlimits=None, attrs=None, bins=None, twin_df=None,
                twin_attrs=None):
    # x=hour is experimental
    import seaborn as sns
    from matplotlib.ticker import MultipleLocator
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.stats import kurtosis
    from scipy.stats import skew
    # df = da_ts.to_dataframe()
    if x == 'month':
        df[x] = df.index.month
        pal = sns.color_palette("Paired", 12)
    elif x == 'hour':
        df[x] = df.index.hour
        if twin_df is not None:
            twin_df[x] = twin_df.index.hour
        # df[x] = df.index
        pal = sns.color_palette("Paired", 12)
    y = df.columns[0]
    if ax is None:
        fig, ax = plt.subplots()
    if kind is None:
        df = df.groupby(x).mean()
        df.plot(ax=ax, legend=False, marker=marker)
        if twin_df is not None:
            twin_df = twin_df.groupby(x).mean()
            twinx = ax.twinx()
            twin_df.plot.line(ax=twinx, color='r', marker='s')
            ax.axhline(0, color='k', linestyle='--')
            if twin_attrs is not None:
                twinx.set_ylabel(twin_attrs['ylabel'])
            align_yaxis(ax, 0, twinx, 0)
        ax.set_xlabel('Time of day [UTC]')
    elif kind == 'violin':
        sns.violinplot(ax=ax, data=df, x=x, y=y, palette=pal, fliersize=4,
                       gridsize=250, inner='quartile', scale='area')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xlabel('')
    elif kind == 'box':
        kwargs = dict(markerfacecolor='r', marker='o')
        sns.boxplot(ax=ax, data=df, x=x, y=y, palette=pal, fliersize=4,
                    whis=1.0, flierprops=kwargs,showfliers=False)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xlabel('')
    elif kind == 'hist':
        if bins is None:
            bins = 15
        a = df[y].dropna()
        sns.distplot(ax=ax, a=a, norm_hist=True, bins=bins, axlabel='PW [mm]')
        xmean = df[y].mean()
        xmedian = df[y].median()
        std = df[y].std()
        sk = skew(df[y].dropna().values)
        kurt = kurtosis(df[y].dropna().values)
        # xmode = df[y].mode().median()
        data_x, data_y = ax.lines[0].get_data()
        ymean = np.interp(xmean, data_x, data_y)
        ymed = np.interp(xmedian, data_x, data_y)
        # ymode = np.interp(xmode, data_x, data_y)
        ax.vlines(x=xmean, ymin=0, ymax=ymean, color='r', linestyle='--')
        ax.vlines(x=xmedian, ymin=0, ymax=ymed, color='g', linestyle='-')
        # ax.vlines(x=xmode, ymin=0, ymax=ymode, color='k', linestyle='-')
        # ax.legend(['Mean:{:.1f}'.format(xmean),'Median:{:.1f}'.format(xmedian),'Mode:{:.1f}'.format(xmode)])
        ax.legend(['Mean: {:.1f}'.format(xmean),'Median: {:.1f}'.format(xmedian)])
        ax.text(0.55, 0.45, "Std-Dev:    {:.1f}\nSkewness: {:.1f}\nKurtosis:   {:.1f}".format(std, sk, kurt),transform=ax.transAxes)
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.grid(True, which='minor', linestyle='--', linewidth=1, alpha=0.7)
    ax.yaxis.grid(True, linestyle='--', linewidth=1, alpha=0.7)
    title = ax.get_title().split('=')[-1].strip(' ')
    if attrs is not None:
        mean_years = float(attrs['mean_years'])
        ax.set_title('')
        ax.text(.2, .85, y.upper(),
                horizontalalignment='center', fontweight='bold',
                transform=ax.transAxes)
        if kind is not None:
            if kind != 'hist':
                ax.text(.22, .72, '{:.1f} years'.format(mean_years),
                        horizontalalignment='center',
                        transform=ax.transAxes)
    ax.yaxis.tick_left()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    if ylimits is not None:
        ax.set_ylim(*ylimits)
        if twin_attrs is not None:
            twinx.set_ylim(*twin_attrs['ylimits'])
            align_yaxis(ax, 0, twinxplot_mea, 0)
    if xlimits is not None:
        ax.set_xlim(*xlimits)
    return ax


def plot_means_pw(load_path=work_yuval, ims_path=ims_path, thresh=50,
                  col_wrap=5, means='hour', save=True):
    import xarray as xr
    import numpy as np
    pw = xr.load_dataset(
            work_yuval /
            'GNSS_PW_thresh_{:.0f}_homogenized.nc'.format(thresh))
    pw = pw[[x for x in pw.data_vars if '_error' not in x]]
    if means == 'hour':
        # remove long term monthly means:
        pw_clim = pw.groupby('time.month') - pw.groupby('time.month').mean('time')    
        pw_clim = pw_clim.groupby('time.{}'.format(means)).mean('time')
    else:
        pw_clim = pw.groupby('time.{}'.format(means)).mean('time')
#    T = xr.load_dataset(
#            ims_path /
#            'GNSS_5mins_TD_ALL_1996_2020.nc')
#    T_clim = T.groupby('time.month').mean('time')
    attrs = [x.attrs for x in pw.data_vars.values()]
    fg = pw_clim.to_array('station').plot(col='station', col_wrap=col_wrap,
                                          color='b', marker='o', alpha=0.7,
                                          sharex=False, sharey=True)
    col_arr = np.arange(0, len(pw_clim))
    right_side = col_arr[col_wrap-1::col_wrap]
    for i, ax in enumerate(fg.axes.flatten()):
        title = ax.get_title().split('=')[-1].strip(' ')
        try:
            mean_years = float(attrs[i]['mean_years'])
            ax.set_title('')
            ax.text(.2, .85, title.upper(),
                    horizontalalignment='center', fontweight='bold',
                    transform=ax.transAxes)
            ax.text(.2, .73, '{:.1f} years'.format(mean_years),
                    horizontalalignment='center',
                    transform=ax.transAxes)
#            ax_t = ax.twinx()
#            T_clim['{}'.format(title)].plot(
#                        color='r', linestyle='dashed', marker='s', alpha=0.7,
#                        ax=ax_t)
#            ax_t.set_ylim(0, 30)
            fg.fig.canvas.draw()

#            labels = [item.get_text() for item in ax_t.get_yticklabels()]
#            ax_t.yaxis.set_ticklabels([])
#            ax_t.tick_params(axis='y', color='r')
#            ax_t.set_ylabel('')
#            if i in right_side:
#                ax_t.set_ylabel(r'Surface temperature [$\degree$C]', fontsize=10)
#                ax_t.yaxis.set_ticklabels(labels)
#                ax_t.tick_params(axis='y', labelcolor='r', color='r')
            # show months ticks and grid lines for pw:
            ax.xaxis.tick_bottom()
            ax.yaxis.tick_left()
            ax.yaxis.grid()
#            ax.legend([ax.lines[0], ax_t.lines[0]], ['PW', 'T'],
#                      loc='upper right', fontsize=10, prop={'size': 8})
#            ax.legend([ax.lines[0]], ['PW'],
#                      loc='upper right', fontsize=10, prop={'size': 8})
        except IndexError:
            pass
    # change bottom xticks to 1-12 and show them:
    # fg.axes[-1, 0].xaxis.set_ticks(np.arange(1, 13))
    [fg.axes[x, 0].set_ylabel('PW [mm]') for x in range(len(fg.axes[:, 0]))]
    # adjust subplots:
    fg.fig.subplots_adjust(top=0.977,
                           bottom=0.039,
                           left=0.036,
                           right=0.959,
                           hspace=0.185,
                           wspace=0.125)
    filename = 'PW_{}_climatology.png'.format(means)
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_gnss_radiosonde_monthly_means(sound_path=sound_path, path=work_yuval,
                                       times=['2014', '2019'], sample='MS',
                                       gps_station='tela', east_height=5000):
    import xarray as xr
    from aux_gps import path_glob
    import pandas as pd
    file = path_glob(sound_path, 'bet_dagan_phys_PW_Tm_Ts_*.nc')
    phys = xr.load_dataset(file[0])['PW']
    if east_height is not None:
        file = path_glob(sound_path, 'bet_dagan_edt_sounding*.nc')
        east = xr.load_dataset(file[0])['east_distance']
        east = east.resample(sound_time=sample).mean().sel(Height=east_height, method='nearest')
        east_df = east.reset_coords(drop=True).to_dataframe()
    if times is not None:
        phys = phys.sel(sound_time=slice(*times))
    ds = phys.resample(sound_time=sample).mean().to_dataset(name='Bet-dagan-radiosonde')
    ds = ds.rename({'sound_time': 'time'})
    gps = xr.load_dataset(path / 'GNSS_PW_thresh_50_homogenized.nc')[gps_station]
    if times is not None:
        gps = gps.sel(time=slice(*times))
    ds[gps_station] = gps.resample(time=sample).mean()
    df = ds.to_dataframe()
    # now plot:
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
    # [x.set_xlim([pd.to_datetime(times[0]), pd.to_datetime(times[1])])
    #  for x in axes]
    df.columns = ['Bet dagan soundings', '{} GNSS station'.format(gps_station)]
    sns.lineplot(data=df, markers=['o','s'],linewidth=2.0, ax=axes[0])
    # axes[0].legend(['Bet_Dagan soundings', 'TELA GPS station'])
    df_r = df.iloc[:, 1] - df.iloc[:, 0]
    df_r.columns = ['Residual distribution']
    sns.lineplot(data=df_r, color='k', marker='o' ,linewidth=1.5, ax=axes[1])
    if east_height is not None:
        ax_east = axes[1].twinx()
        sns.lineplot(data=east_df, color='red', marker='x', linewidth=1.5, ax=ax_east)
        ax_east.set_ylabel('East drift at {} km altitude [km]'.format(east_height / 1000.0))
    axes[1].axhline(y=0, color='r')
    axes[0].grid(b=True, which='major')
    axes[1].grid(b=True, which='major')
    axes[0].set_ylabel('Precipitable Water [mm]')
    axes[1].set_ylabel('Residuals [mm]')
    plt.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=0.01)
    return ds


def plot_wetz_example(path=tela_results_path, plot='WetZ', fontsize=16,
                      save=True):
    from aux_gps import path_glob
    import matplotlib.pyplot as plt
    from gipsyx_post_proc import process_one_day_gipsyx_output
    filepath = path_glob(path, 'tela*_smoothFinal.tdp')[3]
    if plot is None:
        df, meta = process_one_day_gipsyx_output(filepath, True)
        return df, meta
    else:
        df, meta = process_one_day_gipsyx_output(filepath, False)
        if not isinstance(plot, str):
            raise ValueError('pls pick only one field to plot., e.g., WetZ')
    error_plot = '{}_error'.format(plot)
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    desc = meta['desc'][plot]
    unit = meta['units'][plot]
    df[plot].plot(ax=ax, legend=False, color='k')
    ax.fill_between(df.index, df[plot] - df[error_plot],
                    df[plot] + df[error_plot], alpha=0.5)
    ax.grid()
#    ax.set_title('{} from station TELA in {}'.format(
#            desc, df.index[100].strftime('%Y-%m-%d')))
    ax.set_ylabel('WetZ [{}]'.format(unit), fontsize=fontsize)
    ax.set_xlabel('Time [UTC]', fontsize=fontsize)
    ax.tick_params(which='both', labelsize=fontsize)
    ax.grid('on')
    fig.tight_layout()
    filename = 'wetz_tela_daily.png'
    caption('{} from station TELA in {}. Note the error estimation from the GipsyX software(filled)'.format(
            desc, df.index[100].strftime('%Y-%m-%d')))
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return ax


def plot_figure_3(path=tela_solutions, year=2004, field='WetZ',
                  middle_date='11-25', zooms=[10, 3, 0.5], save=True):
    from gipsyx_post_proc import analyse_results_ds_one_station
    import xarray as xr
    import matplotlib.pyplot as plt
    import pandas as pd
    dss = xr.open_dataset(path / 'TELA_ppp_raw_{}.nc'.format(year))
    nums = sorted(list(set([int(x.split('-')[1])
                            for x in dss if x.split('-')[0] == field])))
    ds = dss[['{}-{}'.format(field, i) for i in nums]]
    da = analyse_results_ds_one_station(dss, field=field, plot=False)
    fig, axes = plt.subplots(ncols=1, nrows=3, sharex=False, figsize=(16, 10))
    for j, ax in enumerate(axes):
        start = pd.to_datetime('{}-{}'.format(year, middle_date)
                               ) - pd.Timedelta(zooms[j], unit='D')
        end = pd.to_datetime('{}-{}'.format(year, middle_date)
                             ) + pd.Timedelta(zooms[j], unit='D')
        daa = da.sel(time=slice(start, end))
        for i, ppp in enumerate(ds):
            ds['{}-{}'.format(field, i)].plot(ax=ax, linewidth=3.0)
        daa.plot.line(marker='.', linewidth=0., ax=ax, color='k')
        axes[j].set_xlim(start, end)
        axes[j].set_ylim(daa.min() - 0.5, daa.max() + 0.5)
        try:
            axes[j - 1].axvline(x=start, color='r', alpha=0.85, linestyle='--', linewidth=2.0)
            axes[j - 1].axvline(x=end, color='r', alpha=0.85, linestyle='--', linewidth=2.0)
        except IndexError:
            pass
        units = ds.attrs['{}>units'.format(field)]
        sta = da.attrs['station']
        desc = da.attrs['{}>desc'.format(field)]
        ax.set_ylabel('{} [{}]'.format(field, units))
        ax.set_xlabel('')
        ax.grid()
    # fig.suptitle(
    #     '30 hours stitched {} for GNSS station {}'.format(
    #         desc, sta), fontweight='bold')
    fig.tight_layout()
    caption('20, 6 and 1 days of zenith wet delay in 2004 from the TELA GNSS station for the top, middle and bottom figures respectively. The colored segments represent daily solutions while the black dots represent smoothed mean solutions.')
    filename = 'zwd_tela_discon_panel.png'
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    # fig.subplots_adjust(top=0.95)
    return axes


def plot_figure_3_1(path=work_yuval, data='zwd'):
    import xarray as xr
    from aux_gps import plot_tmseries_xarray
    from PW_stations import load_gipsyx_results
    if data == 'zwd':
        tela = load_gipsyx_results('tela', sample_rate='1H', plot_fields=None)
        label = 'ZWD [cm]'
        title = 'Zenith wet delay derived from GPS station TELA'
        ax = plot_tmseries_xarray(tela, 'WetZ')
    elif data == 'pw':
        ds = xr.open_dataset(path / 'GNSS_hourly_PW.nc')
        tela = ds['tela']
        label = 'PW [mm]'
        title = 'Precipitable water derived from GPS station TELA'
        ax = plot_tmseries_xarray(tela)
    ax.set_ylabel(label)
    ax.set_xlim('1996-02', '2019-07')
    ax.set_title(title)
    ax.set_xlabel('')
    ax.figure.tight_layout()
    return ax


def plot_ts_tm(path=sound_path, model='TSEN',
               times=['2007', '2019'], fontsize=14, save=True):
    """plot ts-tm relashonship"""
    import xarray as xr
    import matplotlib.pyplot as plt
    import seaborn as sns
    from PW_stations import ML_Switcher
    from sklearn.metrics import mean_squared_error
    from sklearn.metrics import r2_score
    import numpy as np
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    from sounding_procedures import get_field_from_radiosonde
    models_dict = {'LR': 'Linear Regression',
                   'TSEN': 'Theil–Sen Regression'}
    # sns.set_style('whitegrid')
    pds = xr.Dataset()
    Ts = get_field_from_radiosonde(path=sound_path, field='Ts',
                                   data_type='phys', reduce=None, times=times,
                                   plot=False)
    Tm = get_field_from_radiosonde(path=sound_path, field='Tm',
                                   data_type='phys', reduce='min', times=times,
                                   plot=False)
    pds['Tm'] = Tm
    pds['Ts'] = Ts
    pds = pds.dropna('sound_time')
    fig, ax = plt.subplots(1, 1, figsize=(7, 7))
    pds.plot.scatter(
        x='Ts',
        y='Tm',
        marker='.',
        s=100.,
        linewidth=0,
        alpha=0.5,
        ax=ax)
    ax.grid()
    ml = ML_Switcher()
    fit_model = ml.pick_model(model)
    X = pds.Ts.values.reshape(-1, 1)
    y = pds.Tm.values
    fit_model.fit(X, y)
    predict = fit_model.predict(X)
    coef = fit_model.coef_[0]
    inter = fit_model.intercept_
    ax.plot(X, predict, c='r')
    bevis_tm = pds.Ts.values * 0.72 + 70.0
    ax.plot(pds.Ts.values, bevis_tm, c='purple')
    ax.legend(['{} ({:.2f}, {:.2f})'.format(models_dict.get(model),
        coef, inter), 'Bevis 1992 et al. (0.72, 70.0)'], fontsize=fontsize-4)
#    ax.set_xlabel('Surface Temperature [K]')
#    ax.set_ylabel('Water Vapor Mean Atmospheric Temperature [K]')
    ax.set_xlabel('Ts [K]', fontsize=fontsize)
    ax.set_ylabel('Tm [K]', fontsize=fontsize)
    ax.set_ylim(265, 320)
    ax.tick_params(labelsize=fontsize)
    axin1 = inset_axes(ax, width="40%", height="40%", loc=2)
    resid = predict - y
    sns.distplot(resid, bins=50, color='k', label='residuals', ax=axin1,
                 kde=False,
                 hist_kws={"linewidth": 1, "alpha": 0.5, "color": "k", 'edgecolor':'k'})
    axin1.yaxis.tick_right()
    rmean = np.mean(resid)
    rmse = np.sqrt(mean_squared_error(y, predict))
    print(rmean, rmse)
    r2 = r2_score(y, predict)
    axin1.axvline(rmean, color='r', linestyle='dashed', linewidth=1)
    # axin1.set_xlabel('Residual distribution[K]')
    textstr = '\n'.join(['n={}'.format(pds.Ts.size),
                         'RMSE: ', '{:.2f} K'.format(rmse)]) # ,
                         # r'R$^2$: {:.2f}'.format(r2)])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    axin1.text(0.05, 0.95, textstr, transform=axin1.transAxes, fontsize=14,
               verticalalignment='top', bbox=props)
#    axin1.text(0.2, 0.9, 'n={}'.format(pds.Ts.size),
#               verticalalignment='top', horizontalalignment='center',
#               transform=axin1.transAxes, color='k', fontsize=10)
#    axin1.text(0.78, 0.9, 'RMSE: {:.2f} K'.format(rmse),
#               verticalalignment='top', horizontalalignment='center',
#               transform=axin1.transAxes, color='k', fontsize=10)
    axin1.set_xlim(-15, 15)
    fig.tight_layout()
    filename = 'Bet_dagan_ts_tm_fit_{}-{}.png'.format(times[0], times[1])
    caption('Water vapor mean temperature (Tm) vs. surface temperature (Ts) of the Bet-Dagan radiosonde station. Ordinary least squares linear fit(red) yields the residual distribution with RMSE of 4 K. Bevis(1992) model is plotted(purple) for comparison.')
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return


def plot_pw_tela_bet_dagan_scatterplot(path=work_yuval, sound_path=sound_path,
                                       ims_path=ims_path, station='tela',
                                       cats=None,
                                       times=['2007', '2019'], wv_name='pw',
                                       r2=False, fontsize=14,
                                       save=True):
    """plot the PW of Bet-Dagan vs. PW of gps station"""
    from PW_stations import mean_ZWD_over_sound_time_and_fit_tstm
    from sklearn.metrics import mean_squared_error
    from sklearn.metrics import r2_score
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    # sns.set_style('white')
    ds, mda = mean_ZWD_over_sound_time_and_fit_tstm(path=path, sound_path=sound_path,
                                                    ims_path=ims_path,
                                                    data_type='phys',
                                                    gps_station=station,
                                                    times=times,
                                                    plot=False,
                                                    cats=cats)
    ds = ds.drop_dims('time')
    time_dim = list(set(ds.dims))[0]
    ds = ds.rename({time_dim: 'time'})
    tpw = 'tpw_bet_dagan'
    ds = ds[[tpw, 'tela_pw']].dropna('time')
    ds = ds.sel(time=slice(*times))
    fig, ax = plt.subplots(1, 1, figsize=(7, 7))
    ds.plot.scatter(x=tpw,
                    y='tela_pw',
                    marker='.',
                    s=100.,
                    linewidth=0,
                    alpha=0.5,
                    ax=ax)
    ax.plot(ds[tpw], ds[tpw], c='r')
    ax.legend(['y = x'], loc='upper right', fontsize=fontsize)
    if wv_name == 'pw':
        ax.set_xlabel('PWV from Bet-Dagan [mm]', fontsize=fontsize)
        ax.set_ylabel('PWV from TELA GPS station [mm]', fontsize=fontsize)
    elif wv_name == 'iwv':
        ax.set_xlabel(r'IWV from Bet-Dagan station [kg$\cdot$m$^{-2}$]', fontsize=fontsize)
        ax.set_ylabel(r'IWV from TELA GPS station [kg$\cdot$m$^{-2}$]', fontsize=fontsize)
    ax.grid()
    axin1 = inset_axes(ax, width="40%", height="40%", loc=2)
    resid = ds.tela_pw.values - ds[tpw].values
    sns.distplot(resid, bins=50, color='k', label='residuals', ax=axin1,
                 kde=False,
                 hist_kws={"linewidth": 1, "alpha": 0.5, "color": "k","edgecolor": 'k'})
    axin1.yaxis.tick_right()
    rmean = np.mean(resid)
    rmse = np.sqrt(mean_squared_error(ds[tpw].values, ds.tela_pw.values))
    r2s = r2_score(ds[tpw].values, ds.tela_pw.values)
    axin1.axvline(rmean, color='r', linestyle='dashed', linewidth=1)
    # axin1.set_xlabel('Residual distribution[mm]')
    ax.tick_params(labelsize=fontsize)
    if wv_name == 'pw':
        if r2:
            textstr = '\n'.join(['n={}'.format(ds[tpw].size),
                                 'bias: {:.2f} mm'.format(rmean),
                                 'RMSE: {:.2f} mm'.format(rmse),
                                 r'R$^2$: {:.2f}'.format(r2s)])
        else:
            textstr = '\n'.join(['n={}'.format(ds[tpw].size),
                                 'bias: {:.2f} mm'.format(rmean),
                                 'RMSE: {:.2f} mm'.format(rmse)])
    elif wv_name == 'iwv':
        if r2:
            textstr = '\n'.join(['n={}'.format(ds[tpw].size),
                                 r'bias: {:.2f} kg$\cdot$m$^{{-2}}$'.format(rmean),
                                 r'RMSE: {:.2f} kg$\cdot$m$^{{-2}}$'.format(rmse),
                                 r'R$^2$: {:.2f}'.format(r2s)])
        else:
            textstr = '\n'.join(['n={}'.format(ds[tpw].size),
                                 r'bias: {:.2f} kg$\cdot$m$^{{-2}}$'.format(rmean),
                                 r'RMSE: {:.2f} kg$\cdot$m$^{{-2}}$'.format(rmse)])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    axin1.text(0.05, 0.95, textstr, transform=axin1.transAxes, fontsize=14,
               verticalalignment='top', bbox=props)
#
#    axin1.text(0.2, 0.95, 'n={}'.format(ds[tpw].size),
#               verticalalignment='top', horizontalalignment='center',
#               transform=axin1.transAxes, color='k', fontsize=10)
#    axin1.text(0.3, 0.85, 'bias: {:.2f} mm'.format(rmean),
#               verticalalignment='top', horizontalalignment='center',
#               transform=axin1.transAxes, color='k', fontsize=10)
#    axin1.text(0.35, 0.75, 'RMSE: {:.2f} mm'.format(rmse),
#               verticalalignment='top', horizontalalignment='center',
#               transform=axin1.transAxes, color='k', fontsize=10)
    # fig.suptitle('Precipitable Water comparison for the years {} to {}'.format(*times))
    fig.tight_layout()
    caption('PW from TELA GNSS station vs. PW from Bet-Dagan radiosonde station in {}-{}. A 45 degree line is plotted(red) for comparison. Note the skew in the residual distribution with an RMSE of 4.37 mm.'.format(times[0], times[1]))
    # fig.subplots_adjust(top=0.95)
    filename = 'Bet_dagan_tela_pw_compare_{}-{}.png'.format(times[0], times[1])
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return ds


def plot_tela_bet_dagan_comparison(path=work_yuval, sound_path=sound_path,
                                   ims_path=ims_path, station='tela',
                                   times=['2007', '2020'], cats=None,
                                   compare='pwv',
                                   save=True):
    from PW_stations import mean_ZWD_over_sound_time_and_fit_tstm
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import matplotlib.dates as mdates
    # sns.set_style('whitegrid')
    ds, mda = mean_ZWD_over_sound_time_and_fit_tstm(path=path,
                                                    sound_path=sound_path,
                                                    ims_path=ims_path,
                                                    data_type='phys',
                                                    gps_station=station,
                                                    times=times,
                                                    plot=False,
                                                    cats=cats)
    ds = ds.drop_dims('time')
    time_dim = list(set(ds.dims))[0]
    ds = ds.rename({time_dim: 'time'})
    ds = ds.dropna('time')
    ds = ds.sel(time=slice(*times))
    if compare == 'zwd':
        df = ds[['zwd_bet_dagan', 'tela']].to_dataframe()
    elif compare == 'pwv':
        df = ds[['tpw_bet_dagan', 'tela_pw']].to_dataframe()
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
    df.columns = ['Bet-Dagan soundings', 'TELA GNSS station']
    sns.scatterplot(
        data=df,
        s=20,
        ax=axes[0],
        style='x',
        linewidth=0,
        alpha=0.8)
    # axes[0].legend(['Bet_Dagan soundings', 'TELA GPS station'])
    df_r = df.iloc[:, 0] - df.iloc[:, 1]
    df_r.columns = ['Residual distribution']
    sns.scatterplot(
        data=df_r,
        color='k',
        s=20,
        ax=axes[1],
        linewidth=0,
        alpha=0.5)
    axes[0].grid(b=True, which='major')
    axes[1].grid(b=True, which='major')
    if compare == 'zwd':
        axes[0].set_ylabel('Zenith Wet Delay [cm]')
        axes[1].set_ylabel('Residuals [cm]')
    elif compare == 'pwv':
        axes[0].set_ylabel('Precipitable Water Vapor [mm]')
        axes[1].set_ylabel('Residuals [mm]')
    # axes[0].set_title('Zenith wet delay from Bet-Dagan radiosonde station and TELA GNSS satation')
    sonde_change_x = pd.to_datetime('2013-08-20')
    axes[1].axvline(sonde_change_x, color='red')
    axes[1].annotate(
        'changed sonde type from VIZ MK-II to PTU GPS',
        (mdates.date2num(sonde_change_x),
         10),
        xytext=(
            15,
            15),
        textcoords='offset points',
        arrowprops=dict(
            arrowstyle='fancy',
            color='red'),
        color='red')
    # axes[1].set_aspect(3)
    [x.set_xlim(*[pd.to_datetime(times[0]), pd.to_datetime(times[1])])
     for x in axes]
    plt.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=0.01)
    filename = 'Bet_dagan_tela_{}_compare.png'.format(compare)
    caption('Top: zenith wet delay from Bet-dagan radiosonde station(blue circles) and from TELA GNSS station(orange x) in 2007-2019. Bottom: residuals. Note the residuals become constrained from 08-2013 probebly due to an equipment change.')
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return df


def plot_israel_map(gis_path=gis_path, rc=rc, ticklabelsize=12, ax=None):
    """general nice map for israel, need that to plot stations,
    and temperature field on top of it"""
    import geopandas as gpd
    import contextily as ctx
    import seaborn as sns
    import cartopy.crs as ccrs
    sns.set_style("ticks", rc=rc)
    isr_with_yosh = gpd.read_file(gis_path / 'Israel_and_Yosh.shp')
    isr_with_yosh.crs = {'init': 'epsg:4326'}
#    isr_with_yosh = isr_with_yosh.to_crs(epsg=3857)
    crs_epsg = ccrs.epsg('3857')
#    crs_epsg = ccrs.epsg('2039')
    if ax is None:
#        fig, ax = plt.subplots(subplot_kw={'projection': crs_epsg},
#                               figsize=(6, 15))
        bounds = isr_with_yosh.geometry.total_bounds
        extent = [bounds[0], bounds[2], bounds[1], bounds[3]]
        # ax.set_extent([bounds[0], bounds[2], bounds[1], bounds[3]], crs=crs_epsg)
        # ax.add_geometries(isr_with_yosh.geometry, crs=crs_epsg)
        ax = isr_with_yosh.plot(alpha=0.0, figsize=(6, 15))
    else:
        isr_with_yosh.plot(alpha=0.0, ax=ax)
    ctx.add_basemap(
            ax,
            url=ctx.sources.ST_TERRAIN_BACKGROUND,
            crs='epsg:4326')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(2))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.tick_params(top=True, bottom=True, left=True, right=True,
                   direction='out', labelsize=ticklabelsize)
#    scale_bar(ax, ccrs.Mercator(), 50, bounds=bounds)
    return ax


def plot_israel_with_stations(gis_path=gis_path, dem_path=dem_path, ims=True,
                              gps=True, radio=True, terrain=True, alt=False,
                              ims_names=False, gps_final=False, save=True):
    from PW_stations import produce_geo_gnss_solved_stations
    from aux_gps import geo_annotate
    from ims_procedures import produce_geo_ims
    import matplotlib.pyplot as plt
    import xarray as xr
    import pandas as pd
    import geopandas as gpd
    ax = plot_israel_map(gis_path)
    station_names = []
    legend = []
    if ims:
        print('getting IMS temperature stations metadata...')
        ims_t = produce_geo_ims(path=gis_path, freq='10mins', plot=False)
        ims_t.plot(ax=ax, color='red', edgecolor='black', alpha=0.5)
        station_names.append('ims')
        legend.append('IMS stations')
        if ims_names:
            geo_annotate(ax, ims_t.lon, ims_t.lat,
                         ims_t['name_english'], xytext=(3, 3), fmt=None,
                         c='k', fw='normal', fs=7, colorupdown=False)
    # ims, gps = produce_geo_df(gis_path=gis_path, plot=False)
    if gps:
        print('getting solved GNSS israeli stations metadata...')
        gps_df = produce_geo_gnss_solved_stations(path=gis_path, plot=False)
        if gps_final:
            to_drop = ['gilb', 'lhav', 'hrmn', 'nizn', 'spir']
            gps_final_stations = [x for x in gps_df.index if x not in to_drop]
            gps = gps_df.loc[gps_final_stations,:]
        gps.plot(ax=ax, color='k', edgecolor='black', marker='s')
        gps_stations = [x for x in gps.index]
        to_plot_offset = ['gilb', 'lhav']
        # [gps_stations.remove(x) for x in to_plot_offset]
        gps_normal_anno = gps.loc[gps_stations, :]
        # gps_offset_anno = gps.loc[to_plot_offset, :]
        geo_annotate(ax, gps_normal_anno.lon, gps_normal_anno.lat,
                     gps_normal_anno.index.str.upper(), xytext=(3, 3), fmt=None,
                     c='k', fw='bold', fs=10, colorupdown=False)
        if alt:
            geo_annotate(ax, gps_normal_anno.lon, gps_normal_anno.lat,
                         gps_normal_anno.alt, xytext=(4, -6), fmt='{:.0f}',
                         c='k', fw='bold', fs=9, colorupdown=False)
#        geo_annotate(ax, gps_offset_anno.lon, gps_offset_anno.lat,
#                     gps_offset_anno.index.str.upper(), xytext=(4, -6), fmt=None,
#                     c='k', fw='bold', fs=10, colorupdown=False)
        station_names.append('gps')
        legend.append('GNSS stations')
    if terrain:
        # overlay with dem data:
        cmap = plt.get_cmap('terrain', 41)
        dem = xr.open_dataarray(dem_path / 'israel_dem_250_500.nc')
        # dem = xr.open_dataarray(dem_path / 'israel_dem_500_1000.nc')
        fg = dem.plot.imshow(ax=ax, alpha=0.5, cmap=cmap,
                             vmin=dem.min(), vmax=dem.max(), add_colorbar=False)
        cbar_kwargs = {'fraction': 0.1, 'aspect': 50, 'pad': 0.03}
        cb = plt.colorbar(fg, **cbar_kwargs)
        cb.set_label(label='meters above sea level', size=8, weight='normal')
        cb.ax.tick_params(labelsize=8)
        ax.set_xlabel('')
        ax.set_ylabel('')
    if radio:   # plot bet-dagan:
        df = pd.Series([32.00, 34.81]).to_frame().T
        df.index = ['Bet-Dagan']
        df.columns = ['lat', 'lon']
        bet_dagan = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon,
                                                                     df.lat),
                                     crs=gps.crs)
        bet_dagan.plot(ax=ax, color='black', edgecolor='black',
                       marker='+')
        geo_annotate(ax, bet_dagan.lon, bet_dagan.lat,
                     bet_dagan.index, xytext=(4, -6), fmt=None,
                     c='k', fw='bold', fs=10, colorupdown=False)
        station_names.append('radio')
        legend.append('radiosonde')
    if legend:
        plt.legend(legend, loc='upper left')
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.05)
    if station_names:
        station_names = '_'.join(station_names)
    else:
        station_names = 'no_stations'
    filename = 'israel_map_{}.png'.format(station_names)
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return ax


def plot_zwd_lapse_rate(path=work_yuval, fontsize=18, model='TSEN', save=True):
    from PW_stations import calculate_zwd_altitude_fit
    df, zwd_lapse_rate = calculate_zwd_altitude_fit(path=path, model=model,
                                                    plot=True, fontsize=fontsize)
    if save:
        filename = 'zwd_lapse_rate.png'
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return


def plot_ims_T_lapse_rate(ims_path=ims_path, dt='2013-10-19T22:00:00',
                          fontsize=16, save=True):
    from aux_gps import path_glob
    import xarray as xr
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    # from matplotlib import rc

    def choose_dt_and_lapse_rate(tdf, dt, T_alts, lapse_rate):
        ts = tdf.loc[dt, :]
        # dt_col = dt.strftime('%Y-%m-%d %H:%M')
        # ts.name = dt_col
        # Tloc_df = Tloc_df.join(ts, how='right')
        # Tloc_df = Tloc_df.dropna(axis=0)
        ts_vs_alt = pd.Series(ts.values, index=T_alts)
        ts_vs_alt_for_fit = ts_vs_alt.dropna()
        [a, b] = np.polyfit(ts_vs_alt_for_fit.index.values,
                            ts_vs_alt_for_fit.values, 1)
        if lapse_rate == 'auto':
            lapse_rate = np.abs(a) * 1000
            if lapse_rate < 5.0:
                lapse_rate = 5.0
            elif lapse_rate > 10.0:
                lapse_rate = 10.0
        return ts_vs_alt, lapse_rate

    # rc('text', usetex=False)
    # rc('text',latex.unicode=False)
    glob_str = 'IMS_TD_israeli_10mins*.nc'
    file = path_glob(ims_path, glob_str=glob_str)[0]
    ds = xr.open_dataset(file)
    time_dim = list(set(ds.dims))[0]
    # slice to a starting year(1996?):
    ds = ds.sel({time_dim: slice('1996', None)})
    # years = sorted(list(set(ds[time_dim].dt.year.values)))
    # get coords and alts of IMS stations:
    T_alts = np.array([ds[x].attrs['station_alt'] for x in ds])
#    T_lats = np.array([ds[x].attrs['station_lat'] for x in ds])
#    T_lons = np.array([ds[x].attrs['station_lon'] for x in ds])
    print('loading IMS_TD of israeli stations 10mins freq..')
    # transform to dataframe and add coords data to df:
    tdf = ds.to_dataframe()
    # dt_col = dt.strftime('%Y-%m-%d %H:%M')
    dt = pd.to_datetime(dt)
    # prepare the ims coords and temp df(Tloc_df) and the lapse rate:
    ts_vs_alt, lapse_rate = choose_dt_and_lapse_rate(tdf, dt, T_alts, 'auto')
    fig, ax_lapse = plt.subplots(figsize=(10, 6))
    sns.regplot(x=ts_vs_alt.index, y=ts_vs_alt.values, color='r',
                scatter_kws={'color': 'k'}, ax=ax_lapse)
    # suptitle = dt.strftime('%Y-%m-%d %H:%M')
    ax_lapse.set_xlabel('Altitude [m]', fontsize=fontsize)
    ax_lapse.set_ylabel(r'Temperature [$\degree$C]', fontsize=fontsize)
    ax_lapse.text(0.5, 0.95, r'Lapse rate: {:.2f} $\degree$C/km'.format(lapse_rate),
                  horizontalalignment='center', verticalalignment='center',
                  fontsize=fontsize,
                  transform=ax_lapse.transAxes, color='k')
    ax_lapse.grid()
    ax_lapse.tick_params(labelsize=fontsize)
    # ax_lapse.set_title(suptitle, fontsize=14, fontweight='bold')
    fig.tight_layout()
    filename = 'ims_lapse_rate_example.png'
    caption('Temperature vs. altitude for 10 PM in 2013-10-19 for all automated 10 mins IMS stations. The lapse rate is calculated using ordinary least squares linear fit.')
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return ax_lapse


def plot_figure_9(hydro_path=hydro_path, gis_path=gis_path, pw_anom=False,
                  max_flow_thresh=None, wv_name='pw', save=True):
    from hydro_procedures import get_hydro_near_GNSS
    from hydro_procedures import loop_over_gnss_hydro_and_aggregate
    import matplotlib.pyplot as plt
    df = get_hydro_near_GNSS(
        radius=5,
        hydro_path=hydro_path,
        gis_path=gis_path,
        plot=False)
    ds = loop_over_gnss_hydro_and_aggregate(df, pw_anom=pw_anom,
                                            max_flow_thresh=max_flow_thresh,
                                            hydro_path=hydro_path,
                                            work_yuval=work_yuval, ndays=3,
                                            plot=False, plot_all=False)
    names = [x for x in ds.data_vars]
    fig, ax = plt.subplots(figsize=(10, 6))
    for name in names:
        ds.mean('station').mean('tide_start')[name].plot.line(
            marker='.', linewidth=0., ax=ax)
    ax.set_xlabel('Days before tide event')
    ax.grid()
    hstations = [ds[x].attrs['hydro_stations'] for x in ds.data_vars]
    events = [ds[x].attrs['total_events'] for x in ds.data_vars]
    fmt = list(zip(names, hstations, events))
    ax.legend(['{} with {} stations ({} total events)'.format(x, y, z)
               for x, y, z in fmt])
    fig.canvas.draw()
    labels = [item.get_text() for item in ax.get_xticklabels()]
    xlabels = [x.replace('−', '') for x in labels]
    ax.set_xticklabels(xlabels)
    fig.canvas.draw()
    if wv_name == 'pw':
        if pw_anom:
            ax.set_ylabel('PW anomalies [mm]')
        else:
            ax.set_ylabel('PW [mm]')
    elif wv_name == 'iwv':
        if pw_anom:
            ax.set_ylabel(r'IWV anomalies [kg$\cdot$m$^{-2}$]')
        else:
            ax.set_ylabel(r'IWV [kg$\cdot$m$^{-2}$]')
    fig.tight_layout()
#    if pw_anom:
#        title = 'Mean PW anomalies for tide stations near all GNSS stations'
#    else:
#        title = 'Mean PW for tide stations near all GNSS stations'
#    if max_flow_thresh is not None:
#        title += ' (max_flow > {} m^3/sec)'.format(max_flow_thresh)
#    ax.set_title(title)
    if pw_anom:
        filename = 'hydro_tide_lag_pw_anom.png'
        if max_flow_thresh:
            filename = 'hydro_tide_lag_pw_anom_max{}.png'.format(max_flow_thresh)
    else:
        filename = 'hydro_tide_lag_pw.png'
        if max_flow_thresh:
            filename = 'hydro_tide_lag_pw_anom_max{}.png'.format(max_flow_thresh)
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return ax


def produce_table_1(removed=['hrmn', 'nizn', 'spir'], merged={'klhv': ['klhv', 'lhav'],
                    'mrav': ['gilb', 'mrav']}, add_loaction=False,
                    scope='annual', remove_distance=True):
    """for scope='diurnal' use removed=['hrmn'], add_location=True
    and remove_distance=False"""
    from PW_stations import produce_geo_gnss_solved_stations
    import pandas as pd
    sites = group_sites_to_xarray(upper=False, scope=scope) 
    df_gnss = produce_geo_gnss_solved_stations(plot=False,
                                               add_distance_to_coast=True)
    new = sites.T.values.ravel()
    if scope == 'annual':
            new = [x for x in new.astype(str) if x != 'nan']
    df_gnss = df_gnss.reindex(new)
    df_gnss['ID'] = df_gnss.index.str.upper()
    pd.options.display.float_format = '{:.2f}'.format
    df = df_gnss[['name', 'ID', 'lat', 'lon', 'alt', 'distance']]
    df['alt'] = df['alt'].map('{:,.0f}'.format)
    df['distance'] = df['distance'].astype(int)
    cols = ['GNSS Station name', 'Station ID', 'Latitude [N]',
            'Longitude [E]', 'Altitude [m a.s.l]', 'Distance from shore [km]']
    df.columns = cols
    df.loc['spir', 'GNSS Station name'] = 'Sapir'
    if add_loaction:
        groups = group_sites_to_xarray(upper=False, scope=scope)
        df.loc[groups.sel(group='coastal').values, 'Location'] = 'coastal'
        df.loc[groups.sel(group='highland').values, 'Location'] = 'highland'
        df.loc[groups.sel(group='eastern').values, 'Location'] = 'eastern'
    if removed is not None:
        df = df.loc[[x for x in df.index if x not in removed], :]
    if remove_distance:
        df = df.iloc[:, 0:-1]
    if merged is not None:
        return df
    print(df.to_latex(index=False))
    return df


def produce_table_stats(thresh=50):
    from PW_stations import produce_pw_statistics
    import xarray as xr
    sites = group_sites_to_xarray(upper=False, scope='annual') 
    new = sites.T.values.ravel()
    sites = group_sites_to_xarray(upper=False, scope='annual')
    new = [x for x in new.astype(str) if x != 'nan']
    pw_mm = xr.load_dataset(
            work_yuval /
             'GNSS_PW_monthly_thresh_{:.0f}_homogenized.nc'.format(thresh))
    
    pw_mm = pw_mm[new]
    df = produce_pw_statistics(thresh=thresh, resample_to_mm=False
                               , pw_input=pw_mm)
    print(df.to_latex(index=False))
    return df


def produce_table_mann_kendall(thresh=50, season=None, with_original=False):
    from PW_stations import mann_kendall_trend_analysis
    import xarray as xr
    import pandas as pd

    def process_mkt(ds_in, alpha=0.05, seasonal=False, factor=120,
                    season_selection=season):
        """because the data is in monthly means and the output is #/decade,
        the factor is 12 months a year and 10 years in a decade yielding 120"""
        ds = ds_in.map(
            mann_kendall_trend_analysis,
            alpha=alpha,
            seasonal=seasonal,
            verbose=False, season_selection=season)
        ds = ds.rename({'dim_0': 'mkt'})
        df = ds.to_dataframe().T
        df = df.drop(['test_name', 'trend', 'h', 'z', 's', 'var_s'], axis=1)
        df['id'] = df.index.str.upper()
        df = df[['id', 'Tau', 'p', 'slope']]
        df.index.name = ''
        df['slope'] = df['slope'] * factor
        numeric_slope_per_factor = df['slope'].copy()
        df['slope'] = df['slope'][df['p'] < 0.05]
        df.loc[:, 'p'][df['p'] < 0.0001] = '<0.0001'
        df['p'][df['p'] != '<0.0001'] = df['p'][df['p'] !=
                                                '<0.0001'].astype(float).map('{:,.4f}'.format)
        df['Tau'] = df['Tau'].map('{:,.4f}'.format)
        df['slope'] = df['slope'].map('{:,.2f}'.format)
        df['slope'][df['slope'] == 'nan'] = '-'
        df.columns = ['Site ID', "Kendall's Tau", 'P-value', "Sen's slope"]
        return df, numeric_slope_per_factor
    
    anoms = xr.load_dataset(
            work_yuval /
             'GNSS_PW_monthly_anoms_thresh_{:.0f}_homogenized.nc'.format(thresh))
    mm = xr.load_dataset(
        work_yuval /
        'GNSS_PW_monthly_thresh_{:.0f}_homogenized.nc'.format(thresh))
    original_anoms =  xr.load_dataset(
            work_yuval /
             'GNSS_PW_monthly_anoms_thresh_{:.0f}.nc'.format(thresh))
    df_original_anoms, _ = process_mkt(original_anoms)
    df_anoms, slope = process_mkt(anoms)
    df_mm, _ = process_mkt(mm, seasonal=True)
    gr = group_sites_to_xarray(scope='annual')
    new = [x for x in gr.T.values.ravel() if isinstance(x, str)]
    df_original_anoms = df_original_anoms.reindex(new)
    df_anoms = df_anoms.reindex(new)
    df_mm = df_mm.reindex(new)
    df_anoms['Percent change'] = 100 * slope / mm.to_dataframe().mean()
    df_anoms['Percent change'] = df_anoms['Percent change'].map('{:,.1f}'.format)
    df_anoms['Percent change'] = df_anoms[df_anoms["Sen's slope"] != '-']['Percent change']
    df_anoms['Percent change'] = df_anoms['Percent change'].fillna('-')
#    mkt_trends = [anoms[x].attrs['mkt_trend'] for x in anoms.data_vars]
#    mkt_bools = [anoms[x].attrs['mkt_h'] for x in anoms.data_vars]
#    mkt_slopes = [anoms[x].attrs['mkt_slope'] for x in anoms.data_vars]
#    mkt_pvalue = [anoms[x].attrs['mkt_p'] for x in anoms.data_vars]
#    mkt_95_lo = [anoms[x].attrs['mkt_trend_95'][0] for x in anoms.data_vars]
#    mkt_95_up = [anoms[x].attrs['mkt_trend_95'][1] for x in anoms.data_vars]
#    df = pd.DataFrame(mkt_trends, index=[x for x in anoms.data_vars], columns=['mkt_trend'])
#    df['mkt_h'] = mkt_bools
#    # transform into per decade:
#    df['mkt_slope'] = mkt_slopes
#    df['mkt_pvalue'] = mkt_pvalue
#    df['mkt_95_lo'] = mkt_95_lo
#    df['mkt_95_up'] = mkt_95_up
#    df[['mkt_slope', 'mkt_95_lo', 'mkt_95_up']] *= 120
#    df.index = df.index.str.upper()
#    df['Sen\'s slope'] = df['mkt_slope'].map('{:,.2f}'.format)
#    df.loc[:, 'Sen\'s slope'][~df['mkt_h']] = 'No trend'
#    con = ['({:.2f}, {:.2f})'.format(x, y) for (x, y) in list(
#        zip(df['mkt_95_lo'].values, df['mkt_95_up'].values))]
#    df['95% confidence intervals'] = con
#    df.loc[:, '95% confidence intervals'][~df['mkt_h']] = '-'
#    df = df[['Sen\'s slope', '95% confidence intervals']]
    print(df_anoms.to_latex(index=False))
    if with_original:
        df = pd.concat([df_anoms, df_original_anoms], axis=1)
        return df
    return df_anoms, df_mm


def plot_peak_hour_distance(path=work_yuval, season='JJA',
                            remove_station='dsea', fontsize=22, save=True):
    from PW_stations import produce_geo_gnss_solved_stations
    from aux_gps import groupby_half_hour_xr
    from aux_gps import xr_reindex_with_date_range
    import xarray as xr
    import pandas as pd
    import seaborn as sns
    import numpy as np
    from sklearn.metrics import r2_score
    pw = xr.open_dataset(path / 'GNSS_PW_thresh_50_for_diurnal_analysis.nc')
    pw = pw[[x for x in pw if '_error' not in x]]
    pw.load()
    pw = pw.sel(time=pw['time.season'] == season)
    pw = pw.map(xr_reindex_with_date_range)
    df = groupby_half_hour_xr(pw)
    halfs = [df.isel(half_hour=x)['half_hour'] for x in df.argmax().values()]
    names = [x for x in df]
    dfh = pd.DataFrame(halfs, index=names)
    geo = produce_geo_gnss_solved_stations(
        add_distance_to_coast=True, plot=False)
    geo['phase'] = dfh
    geo = geo.dropna()
    groups = group_sites_to_xarray(upper=False, scope='diurnal')
    geo.loc[groups.sel(group='coastal').values, 'group'] = 'coastal'
    geo.loc[groups.sel(group='highland').values, 'group'] = 'highland'
    geo.loc[groups.sel(group='eastern').values, 'group'] = 'eastern'
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.grid()
    if remove_station is not None:
        removed = geo.loc[remove_station].to_frame().T
        geo = geo.drop(remove_station, axis=0)
#     lnall = sns.scatterplot(data=geo.loc[only], x='distance', y='phase', ax=ax, hue='group', s=100)
#    geo['phase'] = pd.to_timedelta(geo['phase'], unit='H')
    coast = geo[geo['group'] == 'coastal']
    yerr = 1.0
    lncoast = ax.errorbar(x=coast.loc[:,
                                      'distance'],
                          y=coast.loc[:,
                                      'phase'],
                          yerr=yerr,
                          marker='o',
                          ls='',
                          capsize=2.5,
                          elinewidth=2.5,
                          markeredgewidth=2.5,
                          color='b')
    # lncoast = ax.scatter(coast.loc[:, 'distance'], coast.loc[:, 'phase'], color='b', s=50)
    highland = geo[geo['group'] == 'highland']
#    lnhighland = ax.scatter(highland.loc[:, 'distance'], highland.loc[:, 'phase'], color='brown', s=50)
    lnhighland = ax.errorbar(x=highland.loc[:,
                                            'distance'],
                             y=highland.loc[:,
                                            'phase'],
                             yerr=yerr,
                             marker='o',
                             ls='',
                             capsize=2.5,
                             elinewidth=2.5,
                             markeredgewidth=2.5,
                             color='brown')
    eastern = geo[geo['group'] == 'eastern']
#    lneastern = ax.scatter(eastern.loc[:, 'distance'], eastern.loc[:, 'phase'], color='green', s=50)
    lneastern = ax.errorbar(x=eastern.loc[:,
                                          'distance'],
                            y=eastern.loc[:,
                                          'phase'],
                            yerr=yerr,
                            marker='o',
                            ls='',
                            capsize=2.5,
                            elinewidth=2.5,
                            markeredgewidth=2.5,
                            color='green')
    lnremove = ax.scatter(
        removed.loc[:, 'distance'], removed.loc[:, 'phase'], marker='x', color='k', s=50)
    ax.legend([lncoast,
               lnhighland,
               lneastern,
               lnremove],
              ['Coastal stations',
               'Highland stations',
               'Eastern stations',
               'DSEA station'],
              fontsize=fontsize)
    params = np.polyfit(geo['distance'].values, geo.phase.values, 1)
    params2 = np.polyfit(geo['distance'].values, geo.phase.values, 2)
    x = np.linspace(0, 210, 100)
    y = np.polyval(params, x)
    y2 = np.polyval(params2, x)
    r2 = r2_score(geo.phase.values, np.polyval(params, geo['distance'].values))
    ax.plot(x, y, color='k')
    textstr = '\n'.join([r'R$^2$: {:.2f}'.format(r2)])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.5, 0.95, textstr, transform=ax.transAxes, fontsize=fontsize,
            verticalalignment='top', bbox=props)
    # ax.plot(x,y2, color='green')
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.set_xlabel('Distance from shore [km]', fontsize=fontsize)
    ax.set_ylabel('Peak hour [UTC]', fontsize=fontsize)
    # add sunrise UTC hour
    ax.axhline(16.66, color='tab:orange', linewidth=2)
    # change yticks to hours minuets:
    fig.canvas.draw()
    labels = [item.get_text() for item in ax.get_yticklabels()]
    labels = [pd.to_timedelta(float(x), unit='H') for x in labels]
    labels = ['{}:{}'.format(x.components[1], x.components[2])
              if x.components[2] != 0 else '{}:00'.format(x.components[1]) for x in labels]
    ax.set_yticklabels(labels)
    fig.canvas.draw()
    ax.tick_params(axis='both', which='major', labelsize=fontsize)
    if save:
        filename = 'pw_peak_distance_shore.png'
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return ax


def plot_monthly_means_anomalies_with_station_mean(load_path=work_yuval,
                                                   thresh=50, save=True,
                                                   anoms=None, agg='mean', fontsize=16):
    import xarray as xr
    import seaborn as sns
    from palettable.scientific import diverging as divsci
    import numpy as np
    import matplotlib.dates as mdates
    import pandas as pd
    div_cmap = divsci.Vik_20.mpl_colormap
    if anoms is None:
        anoms = xr.load_dataset(
                load_path /
                'GNSS_PW_monthly_anoms_thresh_{:.0f}_homogenized.nc'.format(thresh))
    df = anoms.to_dataframe()
    sites = group_sites_to_xarray(upper=True, scope='annual').T
    sites_flat = [x.lower() for x in sites.values.flatten() if isinstance(x, str)]
    df = df[sites_flat]
    df.columns = [x.upper() for x in df.columns]
    fig = plt.figure(figsize=(20, 10))
    grid = plt.GridSpec(
        2, 1, height_ratios=[
            2, 1], hspace=0)
    ax_heat = fig.add_subplot(grid[0, 0])  # plt.subplot(221)
    ax_group = fig.add_subplot(grid[1, 0])  # plt.subplot(223)
    cbar_ax = fig.add_axes([0.95, 0.37, 0.01, 0.62])  #[left, bottom, width,
    # height]
    ax_heat = sns.heatmap(
            df.T,
            center=0.0,
            cmap=div_cmap,
            yticklabels=True,
            ax=ax_heat,
            cbar_ax=cbar_ax,
            cbar_kws={'label': 'PWV anomalies [mm]'}, xticklabels=False)
    cbar_ax.set_ylabel('PWV anomalies [mm]', fontsize=fontsize)
    cbar_ax.tick_params(labelsize=fontsize)
    # activate top ticks and tickslabales:
    ax_heat.xaxis.set_tick_params(bottom='off', labelbottom='off', labelsize=fontsize)
    # emphasize the yticklabels (stations):
    ax_heat.yaxis.set_tick_params(left='on')
    ax_heat.set_yticklabels(ax_heat.get_ymajorticklabels(),
                            fontweight='bold', fontsize=fontsize)
    if agg == 'mean':
        ts = df.T.mean().shift(periods=-1, freq='15D')
    elif agg == 'median':
        ts = df.T.median().shift(periods=-1, freq='15D')
    ts.index.name = ''
    # dt_as_int = [x for x in range(len(ts.index))]
    # xticks_labels = ts.index.strftime('%Y-%m').values[::6]
    # xticks = dt_as_int[::6]
    # xticks = ts.index
    # ts.index = dt_as_int
    ts.plot(ax=ax_group, color='k', fontsize=fontsize)
    # group_limit = ax_heat.get_xlim()
    ax_group.set_xlim(ts.index.min(), ts.index.max() +
                      pd.Timedelta(15, unit='D'))
    ax_group.set_ylabel('PWV {} anomalies [mm]'.format(agg), fontsize=fontsize)
    # set ticks and align with heatmap axis (move by 0.5):
    # ax_group.set_xticks(dt_as_int)
    # offset = 1
#    ax_group.xaxis.set(ticks=np.arange(offset / 2.,
#                                       max(dt_as_int) + 1 - min(dt_as_int),
#                                       offset),
#                       ticklabels=dt_as_int)
    # move the lines also by 0.5 to align with heatmap:
    # lines = ax_group.lines  # get the lines
    # [x.set_xdata(x.get_xdata() - min(dt_as_int) + 0.5) for x in lines]
    # ax_group.xaxis.set(ticks=xticks, ticklabels=xticks_labels)
    # ax_group.xaxis.set(ticks=xticks)
    years_fmt = mdates.DateFormatter('%Y')
    ax_group.xaxis.set_major_locator(mdates.YearLocator())
    ax_group.xaxis.set_major_formatter(years_fmt)
    ax_group.xaxis.set_minor_locator(mdates.MonthLocator())
    ax_group.grid()
    # ax_group.axvline('2015-09-15')
    # ax_group.axhline(2.5)
    # plt.setp(ax_group.xaxis.get_majorticklabels(), rotation=45 )
    fig.tight_layout()
    fig.subplots_adjust(right=0.946)
    if save:
        filename = 'pw_monthly_means_anomaly_heatmap.png'
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return ts


def plot_grp_anomlay_heatmap(load_path=work_yuval, gis_path=gis_path,
                             thresh=50, grp='hour', remove_grp=None, season=None,
                             n_clusters=4, save=True, title=False):
    import xarray as xr
    import seaborn as sns
    import numpy as np
    from PW_stations import group_anoms_and_cluster
    from aux_gps import geo_annotate
    import matplotlib.pyplot as plt
    import pandas as pd
    from matplotlib.colors import ListedColormap
    from palettable.scientific import diverging as divsci
    from PW_stations import produce_geo_gnss_solved_stations
    div_cmap = divsci.Vik_20.mpl_colormap
    dem_path = load_path / 'AW3D30'

    def weighted_average(grp_df, weights_col='weights'):
        return grp_df._get_numeric_data().multiply(
            grp_df[weights_col], axis=0).sum() / grp_df[weights_col].sum()

    df, labels_sorted, weights = group_anoms_and_cluster(
            load_path=load_path, thresh=thresh, grp=grp, season=season,
            n_clusters=n_clusters, remove_grp=remove_grp)
    # create figure and subplots axes:
    fig = plt.figure(figsize=(15, 10))
    if title:
        if season is not None:
            fig.suptitle('Precipitable water {}ly anomalies analysis for {} season'.format(grp, season))
        else:
            fig.suptitle('Precipitable water {}ly anomalies analysis (Weighted KMeans {} clusters)'.format(grp, n_clusters))
    grid = plt.GridSpec(
        2, 2, width_ratios=[
            3, 2], height_ratios=[
            4, 1], wspace=0.1, hspace=0)
    ax_heat = fig.add_subplot(grid[0, 0])  # plt.subplot(221)
    ax_group = fig.add_subplot(grid[1, 0])  # plt.subplot(223)
    ax_map = fig.add_subplot(grid[0:, 1])  # plt.subplot(122)
    # get the camp and zip it to groups and produce dictionary:
    cmap = plt.get_cmap("Accent")
    cmap = qualitative_cmap(n_clusters)
    # cmap = plt.get_cmap("Set2_r")
    # cmap = ListedColormap(cmap.colors[::-1])
    groups = list(set(labels_sorted.values()))
    palette = dict(zip(groups, [cmap(x) for x in range(len(groups))]))
    label_cmap_dict = dict(zip(labels_sorted.keys(),
                               [palette[x] for x in labels_sorted.values()]))
    cm = ListedColormap([x for x in palette.values()])
    # plot heatmap and colorbar:
    cbar_ax = fig.add_axes([0.57, 0.24, 0.01, 0.69])  #[left, bottom, width,
    # height]
    ax_heat = sns.heatmap(
            df.T,
            center=0.0,
            cmap=div_cmap,
            yticklabels=True,
            ax=ax_heat,
            cbar_ax=cbar_ax,
            cbar_kws={'label': '[mm]'})
    # activate top ticks and tickslabales:
    ax_heat.xaxis.set_tick_params(top='on', labeltop='on')
    # emphasize the yticklabels (stations):
    ax_heat.yaxis.set_tick_params(left='on')
    ax_heat.set_yticklabels(ax_heat.get_ymajorticklabels(),
                            fontweight = 'bold', fontsize=10)
    # paint ytick labels with categorical cmap:
    boxes = [dict(facecolor=x, boxstyle="square,pad=0.7", alpha=0.6)
             for x in label_cmap_dict.values()]
    ylabels = [x for x in ax_heat.yaxis.get_ticklabels()]
    for label, box in zip(ylabels, boxes):
        label.set_bbox(box)
    # rotate xtick_labels:
#    ax_heat.set_xticklabels(ax_heat.get_xticklabels(), rotation=0,
#                            fontsize=10)
    # plot summed groups (with weights):
    df_groups = df.T
    df_groups['groups'] = pd.Series(labels_sorted)
    df_groups['weights'] = weights
    df_groups = df_groups.groupby('groups').apply(weighted_average)
    df_groups.drop(['groups', 'weights'], axis=1, inplace=True)
    df_groups.T.plot(ax=ax_group, linewidth=2.0, legend=False, cmap=cm)
    if grp == 'hour':
        ax_group.set_xlabel('hour (UTC)')
    ax_group.grid()
    group_limit = ax_heat.get_xlim()
    ax_group.set_xlim(group_limit)
    ax_group.set_ylabel('[mm]')
    # set ticks and align with heatmap axis (move by 0.5):
    ax_group.set_xticks(df.index.values)
    offset = 1
    ax_group.xaxis.set(ticks=np.arange(offset / 2.,
                                       max(df.index.values) + 1 - min(df.index.values),
                                       offset),
                       ticklabels=df.index.values)
    # move the lines also by 0.5 to align with heatmap:
    lines = ax_group.lines  # get the lines
    [x.set_xdata(x.get_xdata() - min(df.index.values) + 0.5) for x in lines]
    # plot israel map:
    ax_map = plot_israel_map(gis_path=gis_path, ax=ax_map)
    # overlay with dem data:
    cmap = plt.get_cmap('terrain', 41)
    dem = xr.open_dataarray(dem_path / 'israel_dem_250_500.nc')
    # dem = xr.open_dataarray(dem_path / 'israel_dem_500_1000.nc')
    im = dem.plot.imshow(ax=ax_map, alpha=0.5, cmap=cmap,
                         vmin=dem.min(), vmax=dem.max(), add_colorbar=False)
    cbar_kwargs = {'fraction': 0.1, 'aspect': 50, 'pad': 0.03}
    cb = fig.colorbar(im, ax=ax_map, **cbar_kwargs)
    # cb = plt.colorbar(fg, **cbar_kwargs)
    cb.set_label(label='meters above sea level', size=8, weight='normal')
    cb.ax.tick_params(labelsize=8)
    ax_map.set_xlabel('')
    ax_map.set_ylabel('')
    print('getting solved GNSS israeli stations metadata...')
    gps = produce_geo_gnss_solved_stations(path=gis_path, plot=False)
    gps.index = gps.index.str.upper()
    gps = gps.loc[[x for x in df.columns], :]
    gps['group'] = pd.Series(labels_sorted)
    gps.plot(ax=ax_map, column='group', categorical=True, marker='o',
             edgecolor='black', cmap=cm, s=100, legend=True, alpha=1.0,
             legend_kwds={'prop': {'size': 10}, 'fontsize': 14,
                          'loc': 'upper left', 'title': 'clusters'})
    # ax_map.set_title('Groupings of {}ly anomalies'.format(grp))
    # annotate station names in map:
    geo_annotate(ax_map, gps.lon, gps.lat,
                 gps.index, xytext=(6, 6), fmt=None,
                 c='k', fw='bold', fs=10, colorupdown=False)
#    plt.legend(['IMS stations', 'GNSS stations'],
#           prop={'size': 10}, bbox_to_anchor=(-0.15, 1.0),
#           title='Stations')
#    plt.legend(prop={'size': 10}, loc='upper left')
    # plt.tight_layout()
    plt.subplots_adjust(top=0.92,
                        bottom=0.065,
                        left=0.065,
                        right=0.915,
                        hspace=0.19,
                        wspace=0.215)
    filename = 'pw_{}ly_anoms_{}_clusters_with_map.png'.format(grp, n_clusters)
    if save:
#        plt.savefig(savefig_path / filename, bbox_inches='tight')
        plt.savefig(savefig_path / filename, orientation='landscape')
    return df


def plot_lomb_scargle(path=work_yuval, save=True):
    from aux_gps import lomb_scargle_xr
    import xarray as xr
    pw_mm = xr.load_dataset(path / 'GNSS_PW_monthly_thresh_50_homogenized.nc')
    pw_mm_median = pw_mm.to_array('station').median('station')
    da = lomb_scargle_xr(
        pw_mm_median.dropna('time'),
        user_freq='MS',
        kwargs={
            'nyquist_factor': 1,
            'samples_per_peak': 100})
    plt.ylabel('')
    plt.title('Lomb–Scargle periodogram')
    plt.xlim([0, 4])
    plt.grid()
    filename = 'Lomb_scargle_monthly_means.png'
    if save:
#        plt.savefig(savefig_path / filename, bbox_inches='tight')
        plt.savefig(savefig_path / filename, orientation='landscape')
    return da


def plot_vertical_climatology_months(path=sound_path, field='Rho_wv',
                                     center_month=7):
    from aux_gps import path_glob
    import xarray as xr
    ds = xr.open_dataset(
        path /
        'bet_dagan_phys_sounding_height_2007-2019.nc')[field]
    fig, ax = plt.subplots(1,2, figsize=(10, 5))
    day = ds.sel(sound_time=ds['sound_time.hour']==12).groupby('sound_time.month').mean('sound_time')
    night = ds.sel(sound_time=ds['sound_time.hour']==00).groupby('sound_time.month').mean('sound_time')
    next_month = center_month + 1
    last_month = center_month - 1
    day = day.sel(month=[last_month, center_month, next_month])
    night = night.sel(month=[last_month, center_month, next_month])
    for month in day.month:
        h=day.sel(month=month)['H-Msl'].values
        rh = day.sel(month=month).values
        ax[0].semilogy(rh, h)
    ax[0].set_title('noon')
    ax[0].set_ylabel('height [m]')
    ax[0].set_xlabel('{}, [{}]'.format(field, day.attrs['units']))
    plt.legend([x for x in ax.lines],[x for x in day.month.values])
    for month in night.month:
        h=night.sel(month=month)['H-Msl'].values
        rh = night.sel(month=month).values
        ax[1].semilogy(rh, h)
    ax[1].set_title('midnight')
    ax[1].set_ylabel('height [m]')
    ax[1].set_xlabel('{}, [{}]'.format(field, night.attrs['units']))
    plt.legend([x for x in ax.lines],[x for x in night.month.values])
    return day, night


def plot_pw_lapse_rate_fit(path=work_yuval, model='TSEN', plot=True):
    from PW_stations import produce_geo_gnss_solved_stations
    import xarray as xr
    from PW_stations import ML_Switcher
    import pandas as pd
    import matplotlib.pyplot as plt
    pw = xr.load_dataset(path / 'GNSS_PW_thresh_50.nc')
    pw = pw[[x for x in pw.data_vars if '_error' not in x]]
    df_gnss = produce_geo_gnss_solved_stations(plot=False)
    df_gnss = df_gnss.loc[[x for x in pw.data_vars], :]
    alt = df_gnss['alt'].values
    # add mean to anomalies:
    pw_new = pw.resample(time='MS').mean()
    pw_mean = pw_new.mean('time')
    # compute std:
#    pw_std = pw_new.std('time')
    pw_std = (pw_new.groupby('time.month') - pw_new.groupby('time.month').mean('time')).std('time')
    pw_vals = pw_mean.to_array().to_dataframe(name='pw')
    pw_vals = pd.Series(pw_vals.squeeze()).values
    pw_std_vals = pw_std.to_array().to_dataframe(name='pw')
    pw_std_vals = pd.Series(pw_std_vals.squeeze()).values
    ml = ML_Switcher()
    fit_model = ml.pick_model(model)
    y = pw_vals
    X = alt.reshape(-1, 1)
    fit_model.fit(X, y)
    predict = fit_model.predict(X)
    coef = fit_model.coef_[0]
    inter = fit_model.intercept_
    pw_lapse_rate = abs(coef)*1000
    if plot:
        fig, ax = plt.subplots(1, 1, figsize=(16, 4))
        ax.errorbar(x=alt, y=pw_vals, yerr=pw_std_vals,
                    marker='.', ls='', capsize=1.5, elinewidth=1.5,
                    markeredgewidth=1.5, color='k')
        ax.grid()
        ax.plot(X, predict, c='r')
        ax.set_xlabel('meters a.s.l')
        ax.set_ylabel('Precipitable Water [mm]')
        ax.legend(['{} ({:.2f} [mm/km], {:.2f} [mm])'.format(model,
                   pw_lapse_rate, inter)])
    return df_gnss['alt'], pw_lapse_rate


def plot_time_series_as_barplot(ts, anoms=False, ts_ontop=None):
    # plt.style.use('fast')
    time_dim = list(set(ts.dims))[0]
    fig, ax = plt.subplots(figsize=(20, 6), dpi=150)
    import matplotlib.dates as mdates
    import matplotlib.ticker
    from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
    import pandas as pd
    if not anoms:
        # sns.barplot(x=ts[time_dim].values, y=ts.values, ax=ax, linewidth=5)
        ax.bar(ts[time_dim].values, ts.values, linewidth=5, width=0.0,
               facecolor='black', edgecolor='black')
        # Series.plot.bar(ax=ax, linewidth=0, width=1)
    else:
        warm = 'tab:orange'
        cold = 'tab:blue'
        positive = ts.where(ts > 0).dropna(time_dim)
        negative = ts.where(ts < 0).dropna(time_dim)
        ax.bar(
            positive[time_dim].values,
            positive.values,
            linewidth=3.0,
            width=1.0,
            facecolor=warm, edgecolor=warm, alpha=1.0)
        ax.bar(
            negative[time_dim].values,
            negative.values,
            width=1.0,
            linewidth=3.0,
            facecolor=cold, edgecolor=cold, alpha=1.0)
    if ts_ontop is not None:
        ax_twin = ax.twinx()
        color = 'red'
        ts_ontop.plot.line(color=color, linewidth=2.0, ax=ax_twin)
        ax_twin.set_ylabel('PW [mm]', color=color)  # we already handled the x-label with ax1
        ax_twin.tick_params(axis='y', labelcolor=color)
        ax_twin.legend(['3-month running mean of PW anomalies'])
        title_add = ' and the median Precipitable Water anomalies from Israeli GNSS sites'
        l2 = ax_twin.get_ylim()
        ax.set_ylim(l2)
    else:
        title_add = ''
        
    ax.grid(None)
    ax.set_xlim([pd.to_datetime('1996'), pd.to_datetime('2020')])
    ax.set_title('Multivariate ENSO Index Version 2 {}'.format(title_add))
    ax.set_ylabel('MEI.v2')
    # ax.xaxis.set_major_locator(MultipleLocator(20))
    # Change minor ticks to show every 5. (20/4 = 5)
#    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    years_fmt = mdates.DateFormatter('%Y')
    # ax.figure.autofmt_xdate()
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_minor_locator(mdates.YearLocator(1)) 
    ax.xaxis.set_major_formatter(years_fmt)

    # ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.figure.autofmt_xdate()
#     plt.tick_params(
#            axis='x',          # changes apply to the x-axis
#            which='both',      # both major and minor ticks are affected
#            bottom=True,      # ticks along the bottom edge are off
#            top=False,         # ticks along the top edge are off
#            labelbottom=True)
    # fig.tight_layout()
    plt.show()
    return


def plot_tide_pw_lags(path=hydro_path, pw_anom=False, rolling='1H', save=True):
    from aux_gps import path_glob
    import xarray as xr
    import numpy as np
    file = path_glob(path, 'PW_tide_sites_*.nc')[-1]
    if pw_anom:
        file = path_glob(path, 'PW_tide_sites_anom_*.nc')[-1]
    ds = xr.load_dataset(file)
    names = [x for x in ds.data_vars]
    fig, ax = plt.subplots(figsize=(8, 6))
    for name in names:
        da = ds.mean('station').mean('tide_start')[name]
        ser = da.to_series()
        if rolling is not None:
            ser = ser.rolling(rolling).mean()
        time=(ser.index / np.timedelta64(1, 'D')).astype(float)
        # ser = ser.loc[pd.Timedelta(-2.2,unit='D'):pd.Timedelta(1, unit='D')]
        ser.index = time

        ser.plot(marker='.', linewidth=0., ax=ax)
    ax.set_xlabel('Days around tide event')
    ax.set_ylabel('PW [mm]')
    hstations = [ds[x].attrs['hydro_stations'] for x in ds.data_vars]
    events = [ds[x].attrs['total_events'] for x in ds.data_vars]
    fmt = list(zip(names, hstations, events))
    ax.legend(['{} with {} stations ({} total events)'.format(x.upper(), y, z)
               for x, y, z in fmt])
    ax.set_xlim([-3, 1])
    ax.axvline(0, color='k', linestyle='--')
    ax.grid()
    filename = 'pw_tide_sites.png'
    if pw_anom:
        filename = 'pw_tide_sites_anom.png'
    if save:
#        plt.savefig(savefig_path / filename, bbox_inches='tight')
        plt.savefig(savefig_path / filename, orientation='landscape')
#    ax.xaxis.set_major_locator(mdates.HourLocator(interval=24)) # tick every two hours
#    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
#    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
#    formatter = mdates.ConciseDateFormatter(locator)
#    ax.xaxis.set_major_locator(locator)
#    ax.xaxis.set_major_formatter(formatter)
    # title = 'Mean PW for tide stations near all GNSS stations'
    # ax.set_title(title)    
    return


def plot_profiler(path=work_yuval, ceil_path=ceil_path, title=False,
                  field='maxsnr', save=True):
    import xarray as xr
    from ceilometers import read_coastal_BL_levi_2011
    from aux_gps import groupby_half_hour_xr
    from calendar import month_abbr
    df = read_coastal_BL_levi_2011(path=ceil_path)
    ds = df.to_xarray()
    pw = xr.open_dataset(path / 'GNSS_PW_thresh_50_for_diurnal_analysis.nc')
    pw = pw['csar']
    pw.load()
    pw = pw.sel(time=pw['time.month']==7).dropna('time')
    pw_size = pw.dropna('time').size
    pwyears = [pw.time.dt.year.min().item(), pw.time.dt.year.max().item()]
    pw_std = groupby_half_hour_xr(pw, reduce='std')['csar']
    pw_hour = groupby_half_hour_xr(pw, reduce='mean')['csar']
    pw_hour_plus = (pw_hour + pw_std).values
    pw_hour_minus = (pw_hour - pw_std).values
    if field == 'maxsnr':
        mlh_hour = ds['maxsnr']
        mlh_std = ds['std_maxsnr']
        label = 'Max SNR'
    elif field == 'tv_inversion':
        mlh_hour = ds['tv_inversion']
        mlh_std = ds['std_tv200']
        label = 'Tv inversion'
    mlh_hour_minus = (mlh_hour - mlh_std).values
    mlh_hour_plus = (mlh_hour + mlh_std).values
    half_hours = pw_hour.half_hour.values
    fig, ax = plt.subplots(figsize=(10, 8))
    red = 'tab:red'
    blue = 'tab:blue'
    pwln = pw_hour.plot(color=blue, marker='s', ax=ax)
    ax.fill_between(half_hours, pw_hour_minus, pw_hour_plus, color=blue, alpha=0.5)
    twin = ax.twinx()
    mlhln = mlh_hour.plot(color=red, marker='o', ax=twin)
    twin.fill_between(half_hours, mlh_hour_minus, mlh_hour_plus, color=red, alpha=0.5)
    pw_label = 'PW: {}-{}, {} ({} pts)'.format(pwyears[0], pwyears[1], month_abbr[7], pw_size)
    mlh_label = 'MLH: {}-{}, {} ({} pts)'.format(1997,1999, month_abbr[7], 90)
#    if month is not None:
#        pwmln = pw_m_hour.plot(color='tab:orange', marker='^', ax=ax)
#        pwm_label = 'PW: {}-{}, {} ({} pts)'.format(pw_years[0], pw_years[1], month_abbr[month], pw_month.dropna('time').size)
#        ax.legend(pwln + mlhln + pwmln, [pw_label, mlh_label, pwm_label], loc=leg_loc)
#    else:
    ax.legend([pwln[0] , mlhln[0]], [pw_label, mlh_label], loc='best')
#    plt.legend([pw_label, mlh_label])
    ax.tick_params(axis='y', colors=blue)
    twin.tick_params(axis='y', colors=red)
    ax.set_ylabel('PW [mm]', color=blue)
    twin.set_ylabel('MLH [m]', color=red)
    twin.set_ylim(400, 1250)
    ax.set_xticks([x for x in range(24)])
    ax.set_xlabel('Hour of day [UTC]')
    ax.grid()
    mlh_name = 'Hadera'
    textstr = '{}, {}'.format(mlh_name, pw.name.upper())
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)
    if title:
        ax.set_title('The diurnal cycle of {} Mixing Layer Height ({}) and {} GNSS site PW'.format(mlh_name, label, pw.name.upper()))
    fig.tight_layout()
    if save:
        filename = 'PW_diurnal_with_MLH_csar_{}.png'.format(field)
        plt.savefig(savefig_path / filename, orientation='landscape')
    return ax


def plot_ceilometers(path=work_yuval, ceil_path=ceil_path, interpolate='6H',
                     fontsize=14, save=True):
    import xarray as xr
    from ceilometers import twin_hourly_mean_plot
    from ceilometers import read_all_ceilometer_stations
    import numpy as np
    pw = xr.open_dataset(path / 'GNSS_PW_thresh_50_for_diurnal_analysis.nc')
    pw = pw[['tela', 'jslm', 'yrcm', 'nzrt', 'klhv', 'csar']]
    pw.load()
    ds = read_all_ceilometer_stations(path=ceil_path)
    if interpolate is not None:
        attrs = [x.attrs for x in ds.data_vars.values()]
        ds = ds.interpolate_na('time', max_gap=interpolate, method='cubic')
        for i, da in enumerate(ds):
            ds[da].attrs.update(attrs[i])
    fig, axes = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(15, 6))
    couples = [['tela', 'TLV'], ['jslm', 'JR']]
    twins = []
    for i, ax in enumerate(axes.flatten()):
        ax, twin = twin_hourly_mean_plot(pw[couples[i][0]],
                                         ds[couples[i][1]],
                                         month=None,
                                         ax=ax,
                                         title=False,
                                         leg_loc='best', fontsize=fontsize)
        twins.append(twin)
        ax.xaxis.set_ticks(np.arange(0, 23, 3))
        ax.grid()
    twin_ylim_min = min(min([x.get_ylim() for x in twins]))
    twin_ylim_max = max(max([x.get_ylim() for x in twins]))
    for twin in twins:
        twin.set_ylim(twin_ylim_min, twin_ylim_max)
    fig.tight_layout()
    filename = 'PW_diurnal_with_MLH_tela_jslm.png'
    if save:
        #        plt.savefig(savefig_path / filename, bbox_inches='tight')
        plt.savefig(savefig_path / filename, orientation='landscape')
    return fig


def plot_field_with_fill_between(da, dim='hour', mean_dim=None, ax=None,
                                 color='b', marker='s'):
    if dim not in da.dims:
        raise KeyError('{} not in {}'.format(dim, da.name))
    if mean_dim is None:
        mean_dim = [x for x in da.dims if dim not in x][0]
    da_mean = da.mean(mean_dim)
    da_std = da.std(mean_dim)
    da_minus = da_mean - da_std
    da_plus = da_mean + da_std
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    line = da_mean.plot(color=color, marker=marker, ax=ax)
    ax.fill_between(da_mean[dim], da_minus, da_plus, color=color, alpha=0.5)
    return line


def plot_hist_with_seasons(da_ts):
    import seaborn as sns
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.kdeplot(da_ts.dropna('time'), ax=ax, color='k')
    sns.kdeplot(
        da_ts.sel(
            time=da_ts['time.season'] == 'DJF').dropna('time'),
        legend=False,
        ax=ax,
        shade=True)
    sns.kdeplot(
        da_ts.sel(
            time=da_ts['time.season'] == 'MAM').dropna('time'),
        legend=False,
        ax=ax,
        shade=True)
    sns.kdeplot(
        da_ts.sel(
            time=da_ts['time.season'] == 'JJA').dropna('time'),
        legend=False,
        ax=ax,
        shade=True)
    sns.kdeplot(
        da_ts.sel(
            time=da_ts['time.season'] == 'SON').dropna('time'),
        legend=False,
        ax=ax,
        shade=True)
    plt.legend(['ALL', 'MAM', 'DJF', 'SON', 'JJA'])
    return


def plot_diurnal_pw_all_seasons(path=work_yuval, season='ALL', synoptic=None,
                                fontsize=20, labelsize=18,
                                ylim=[-2.7, 3.3], save=True):
    import xarray as xr
    from synoptic_procedures import slice_xr_with_synoptic_class
    gnss_filename = 'GNSS_PW_thresh_50_for_diurnal_analysis_removed_daily.nc'
    pw = xr.load_dataset(path / gnss_filename)
    df_annual = pw.groupby('time.hour').mean().to_dataframe()
    if season is None and synoptic is None:
        # plot annual diurnal cycle only:
        fg = plot_pw_geographical_segments(df_annual, fg=None, marker='o', color='b',
                                           ylim=ylim)
        legend = ['Annual']
    elif season == 'ALL' and synoptic is None:
        df_jja = pw.sel(time=pw['time.season'] == 'JJA').groupby(
            'time.hour').mean().to_dataframe()
        df_son = pw.sel(time=pw['time.season'] == 'SON').groupby(
            'time.hour').mean().to_dataframe()
        df_djf = pw.sel(time=pw['time.season'] == 'DJF').groupby(
            'time.hour').mean().to_dataframe()
        df_mam = pw.sel(time=pw['time.season'] == 'MAM').groupby(
            'time.hour').mean().to_dataframe()
        fg = plot_pw_geographical_segments(
            df_jja,
            fg=None,
            marker='s',
            color='tab:green',
            ylim=ylim,
            fontsize=fontsize,
            labelsize=labelsize, zorder=0, label='JJA')
        fg = plot_pw_geographical_segments(
            df_son,
            fg=fg,
            marker='^',
            color='tab:red',
            ylim=ylim,
            fontsize=fontsize,
            labelsize=labelsize, zorder=1, label='SON')
        fg = plot_pw_geographical_segments(
            df_djf,
            fg=fg,
            marker='x',
            color='tab:blue',
            fontsize=fontsize,
            labelsize=labelsize, zorder=2, label='DJF')
        fg = plot_pw_geographical_segments(
            df_mam,
            fg=fg,
            marker='+',
            color='tab:orange',
            ylim=ylim,
            fontsize=fontsize,
            labelsize=labelsize, zorder=4, label='MAM')
        fg = plot_pw_geographical_segments(df_annual, fg=fg, marker='d',
                                           color='tab:purple', ylim=ylim,
                                           fontsize=fontsize,
                                           labelsize=labelsize, zorder=3,
                                           label='Annual')
    elif season is None and synoptic == 'ALL':
        df_pt = slice_xr_with_synoptic_class(
            pw, path=path, syn_class='PT').groupby('time.hour').mean().to_dataframe()
        df_rst = slice_xr_with_synoptic_class(
            pw, path=path, syn_class='RST').groupby('time.hour').mean().to_dataframe()
        df_cl = slice_xr_with_synoptic_class(
            pw, path=path, syn_class='CL').groupby('time.hour').mean().to_dataframe()
        df_h = slice_xr_with_synoptic_class(
            pw, path=path, syn_class='H').groupby('time.hour').mean().to_dataframe()
        fg = plot_pw_geographical_segments(
            df_pt,
            fg=None,
            marker='s',
            color='tab:green',
            ylim=ylim,
            fontsize=fontsize,
            labelsize=labelsize, zorder=0, label='PT')
        fg = plot_pw_geographical_segments(
            df_rst,
            fg=fg,
            marker='^',
            color='tab:red',
            ylim=ylim,
            fontsize=fontsize,
            labelsize=labelsize, zorder=1, label='RST')
        fg = plot_pw_geographical_segments(
            df_cl,
            fg=fg,
            marker='x',
            color='tab:blue',
            fontsize=fontsize,
            labelsize=labelsize, zorder=2, label='CL')
        fg = plot_pw_geographical_segments(
            df_h,
            fg=fg,
            marker='+',
            color='tab:orange',
            ylim=ylim,
            fontsize=fontsize,
            labelsize=labelsize, zorder=4, label='H')
        fg = plot_pw_geographical_segments(df_annual, fg=fg, marker='d',
                                           color='tab:purple', ylim=ylim,
                                           fontsize=fontsize,
                                           labelsize=labelsize, zorder=3,
                                           label='Annual')
    sites = group_sites_to_xarray(False, scope='diurnal')
    for i, (ax, site) in enumerate(zip(fg.axes.flatten(), sites.values.flatten())):
        lns = ax.get_lines()
        if site in ['yrcm']:
            leg_loc = 'upper right'
        elif site in ['nrif', 'elat']:
            leg_loc = 'upper center'
        elif site in ['ramo']:
            leg_loc = 'lower center'
        else:
            leg_loc = None
        # do legend for each panel:
#        ax.legend(
#            lns,
#            legend,
#            prop={
#                'size': 12},
#            framealpha=0.5,
#            fancybox=True,
#            ncol=2,
#            loc=leg_loc, fontsize=12)
    lines_labels = [ax.get_legend_handles_labels() for ax in fg.fig.axes][0]
#    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    fg.fig.legend(lines_labels[0], lines_labels[1], prop={'size': 20},edgecolor='k',
                  framealpha=0.5, fancybox=True, facecolor='white',
                  ncol=5, fontsize=20, loc='upper center', bbox_to_anchor=(0.5, 1.005),
                  bbox_transform=plt.gcf().transFigure)
    fg.fig.subplots_adjust(
        top=0.973,
        bottom=0.029,
        left=0.054,
        right=0.995,
        hspace=0.15,
        wspace=0.12)
    if save:
        filename = 'pw_diurnal_geo_{}.png'.format(season)
#        plt.savefig(savefig_path / filename, bbox_inches='tight')
        plt.savefig(savefig_path / filename, orientation='portrait')
    return fg


def group_sites_to_xarray(upper=False, scope='diurnal'):
    import xarray as xr
    import numpy as np
    if scope == 'diurnal':
        group1 = ['KABR', 'BSHM', 'CSAR', 'TELA', 'ALON', 'SLOM', 'NIZN']
        group2 = ['NZRT', 'MRAV', 'YOSH', 'JSLM', 'KLHV', 'YRCM', 'RAMO']
        group3 = ['ELRO', 'KATZ', 'DRAG', 'DSEA', 'SPIR', 'NRIF', 'ELAT']
    elif scope == 'annual':
        group1 = ['KABR', 'BSHM', 'CSAR', 'TELA', 'ALON', 'SLOM']
        group2 = ['NZRT', 'MRAV', 'YOSH', 'JSLM', 'KLHV', 'YRCM', 'RAMO']
        group3 = ['ELRO', 'KATZ', 'DRAG', 'DSEA', 'NRIF', 'ELAT']
    if not upper:
        group1 = [x.lower() for x in group1]
        group2 = [x.lower() for x in group2]
        group3 = [x.lower() for x in group3]
    gr1 = xr.DataArray(group1, dims='GNSS')
    gr2 = xr.DataArray(group2, dims='GNSS')
    gr3 = xr.DataArray(group3, dims='GNSS')
    gr1['GNSS'] = np.arange(0, len(gr1))
    gr2['GNSS'] = np.arange(0, len(gr2))
    gr3['GNSS'] = np.arange(0, len(gr3))
    sites = xr.concat([gr1, gr2, gr3], 'group').T
    sites['group'] = ['coastal', 'highland', 'eastern']
    return sites


#def plot_diurnal_pw_geographical_segments(df, fg=None, marker='o', color='b',
#                                          ylim=[-2, 3]):
#    import xarray as xr
#    import numpy as np
#    from matplotlib.ticker import MultipleLocator
#    from PW_stations import produce_geo_gnss_solved_stations
#    geo = produce_geo_gnss_solved_stations(plot=False)
#    sites = group_sites_to_xarray(upper=False, scope='diurnal')
#    sites_flat = [x for x in sites.values.flatten() if isinstance(x, str)]
#    da = xr.DataArray([x for x in range(len(sites_flat))], dims='GNSS')
#    da['GNSS'] = [x for x in range(len(da))]
#    if fg is None:
#        fg = xr.plot.FacetGrid(
#            da,
#            col='GNSS',
#            col_wrap=3,
#            sharex=False,
#            sharey=False, figsize=(20, 20))
#    for i in range(fg.axes.shape[0]):  # i is rows
#        for j in range(fg.axes.shape[1]):  # j is cols
#            try:
#                site = sites.values[i, j]
#                ax = fg.axes[i, j]
#                df.loc[:, site].plot(ax=ax, marker=marker, color=color)
#                ax.set_xlabel('Hour of day [UTC]')
#                ax.yaxis.tick_left()
#                ax.grid()
##                ax.spines["top"].set_visible(False)
##                ax.spines["right"].set_visible(False)
##                ax.spines["bottom"].set_visible(False)
#                ax.xaxis.set_ticks(np.arange(0, 23, 3))
#                if j == 0:
#                    ax.set_ylabel('PW anomalies [mm]', fontsize=12)
##                elif j == 1:
##                    if i>5:
##                        ax.set_ylabel('PW anomalies [mm]', fontsize=12)
#                site_label = '{} ({:.0f})'.format(site.upper(), geo.loc[site].alt)
#                ax.text(.12, .85, site_label,
#                        horizontalalignment='center', fontweight='bold',
#                        transform=ax.transAxes)
##                ax.yaxis.set_minor_locator(MultipleLocator(3))
##                ax.yaxis.grid(
##                    True,
##                    which='minor',
##                    linestyle='--',
##                    linewidth=1,
##                    alpha=0.7)
##                ax.yaxis.grid(True, linestyle='--', linewidth=1, alpha=0.7)
#                if ylim is not None:
#                    ax.set_ylim(*ylim)
#            except KeyError:
#                ax.set_axis_off()
##    for i, ax in enumerate(fg.axes[:, 0]):
##        try:
##            df[gr1].iloc[:, i].plot(ax=ax)
##        except IndexError:
##            ax.set_axis_off()
##    for i, ax in enumerate(fg.axes[:, 1]):
##        try:
##            df[gr2].iloc[:, i].plot(ax=ax)
##        except IndexError:
##            ax.set_axis_off()
##    for i, ax in enumerate(fg.axes[:, 2]):
##        try:
##            df[gr3].iloc[:, i].plot(ax=ax)
##        except IndexError:
##            ax.set_axis_off()
#
#    fg.fig.tight_layout()
#    fg.fig.subplots_adjust()
#    return fg

def plot_long_term_anomalies(path=work_yuval, era5_path=era5_path,
                             aero_path=aero_path, save=True):
    import xarray as xr
    from aux_gps import anomalize_xr
    from aeronet_analysis import prepare_station_to_pw_comparison
    # load GNSS Israel:
    pw = xr.load_dataset(path / 'GNSS_PW_monthly_anoms_thresh_50_homogenized.nc')
    pw_mean = pw.to_array('station').mean('station')
    # load ERA5:
    era5 = xr.load_dataset(era5_path/ 'era5_TCWV_israel_1996-2019.nc')
    era5_mean = era5.mean('lat').mean('lon')
    era5_mean = era5_mean.resample(time='MS').mean()
    era5_mean = anomalize_xr(era5_mean, freq='MS')
    # load AERONET:
    aero = prepare_station_to_pw_comparison(path=aero_path, gis_path=gis_path,
                                            station='boker', mm_anoms=True)
    df = pw_mean.to_dataframe(name='GNSS')
    df['ERA5'] = era5_mean['tcwv'].to_dataframe()
    df['AERONET'] = aero.to_dataframe()
    fig, ax = plt.subplots(figsize=(16, 5))
#    df['GNSS'].plot(ax=ax, color='k')
#    df['ERA5'].plot(ax=ax, color='r')
#    df['AERONET'].plot(ax=ax, color='b')
    pwln = pw_mean.plot.line('k-', ax=ax, linewidth=1.5)
    era5ln = era5_mean['tcwv'].plot.line('r--', ax=ax, alpha=0.8)
    aeroln = aero.plot.line('b-.', ax=ax, alpha=0.8)
    era5corr = df.corr().loc['GNSS', 'ERA5']
    aerocorr = df.corr().loc['GNSS', 'AERONET']
    ax.legend(pwln + era5ln + aeroln,
              ['GNSS',
               'ERA5, r={:.2f}'.format(era5corr),
               'AERONET, r={:.2f}'.format(aerocorr)])
    ax.set_ylabel('PW anomalies [mm]')
    ax.set_xlabel('')
    ax.grid()
    ax = fix_time_axis_ticks(ax, limits=['1998-01', '2020-01'])
    fig.tight_layout()
    fig.subplots_adjust(right=0.946)
    if save:
        filename = 'pw_long_term_anomalies.png'
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fig


def plot_pw_geographical_segments(df, scope='diurnal', kind=None, fg=None,
                                  marker='o', color='b', ylim=[-2, 3],
                                  fontsize=14, labelsize=10, zorder=0,
                                  label=None, save=False, bins=None):
    import xarray as xr
    import numpy as np
    from scipy.stats import kurtosis
    from scipy.stats import skew
    from matplotlib.ticker import MultipleLocator
    from PW_stations import produce_geo_gnss_solved_stations
    from matplotlib.ticker import AutoMinorLocator
    from matplotlib.ticker import FormatStrFormatter
    import seaborn as sns
    scope_dict = {'diurnal': {'xticks': np.arange(0, 23, 3),
                              'xlabel': 'Hour of day [UTC]',
                              'ylabel': 'PWV anomalies [mm]',
                              'colwrap': 3},
                  'annual': {'xticks': np.arange(1, 13),
                             'xlabel': 'month',
                             'ylabel': 'PWV [mm]',
                             'colwrap': 3}
                  }
    geo = produce_geo_gnss_solved_stations(plot=False)
    sites = group_sites_to_xarray(upper=False, scope=scope)
#    if scope == 'annual':
#        sites = sites.T
    sites_flat = [x for x in sites.values.flatten() if isinstance(x, str)]
    da = xr.DataArray([x for x in range(len(sites_flat))], dims='GNSS')
    da['GNSS'] = [x for x in range(len(da))]
    if fg is None:
        fg = xr.plot.FacetGrid(
            da,
            col='GNSS',
            col_wrap=scope_dict[scope]['colwrap'],
            sharex=False,
            sharey=False, figsize=(20, 20))
    for i in range(fg.axes.shape[0]):  # i is rows
        for j in range(fg.axes.shape[1]):  # j is cols
            site = sites.values[i, j]
            ax = fg.axes[i, j]
            if not isinstance(site, str):
                ax.set_axis_off()
                continue
            else:
                if kind is None:
                    df[site].plot(ax=ax, marker=marker, color=color,
                      zorder=zorder, label=label)
                    ax.xaxis.set_ticks(scope_dict[scope]['xticks'])
                    ax.grid(which='major')
                    ax.grid(axis='y', which='minor', linestyle='--')
                elif kind == 'violin':
                    df['month'] = df.index.month
                    pal = sns.color_palette("Paired", 12)
                    sns.violinplot(ax=ax, data=df, fliersize=4, x='month',
                                   y=site, palette=pal,
                                   gridsize=250, inner='quartile',
                                   scale='area')
                    ax.set_ylabel('')
                    ax.spines["top"].set_visible(False)
                    ax.spines["right"].set_visible(False)
                    ax.spines["bottom"].set_visible(False)
                    ax.grid(axis='y', which='major')
                    ax.grid(axis='y', which='minor', linestyle='--')
                elif kind == 'hist':
                    if bins is None:
                        bins = 15
                    sns.histplot(ax=ax, data=df[site].dropna(),
                                 line_kws={'linewidth':3}, stat='density', kde=True, bins=bins)
                    ax.set_xlabel('PWV [mm]', fontsize=fontsize)
                    ax.grid()
                    ax.set_ylabel('')
                    xmean = df[site].mean()
                    xmedian = df[site].median()
                    std = df[site].std()
                    sk = skew(df[site].dropna().values)
                    kurt = kurtosis(df[site].dropna().values)
                    # xmode = df[y].mode().median()
                    data_x, data_y = ax.lines[0].get_data()
                    ymean = np.interp(xmean, data_x, data_y)
                    ymed = np.interp(xmedian, data_x, data_y)
                    # ymode = np.interp(xmode, data_x, data_y)
                    ax.vlines(x=xmean, ymin=0, ymax=ymean, color='r', linestyle='--', linewidth=3)
                    ax.vlines(x=xmedian, ymin=0, ymax=ymed, color='g', linestyle='-', linewidth=3)
                    # ax.vlines(x=xmode, ymin=0, ymax=ymode, color='k', linestyle='-')
                    ax.legend(['Mean: {:.1f}'.format(xmean),'Median: {:.1f}'.format(xmedian)], fontsize=fontsize)
#                    ax.text(0.55, 0.45, "Std-Dev:    {:.1f}\nSkewness: {:.1f}\nKurtosis:   {:.1f}".format(std, sk, kurt),transform=ax.transAxes, fontsize=fontsize)
                ax.tick_params(axis='x', which='major', labelsize=labelsize)
                if kind != 'hist':
                    ax.set_xlabel(scope_dict[scope]['xlabel'], fontsize=16)
                ax.yaxis.set_major_locator(plt.MaxNLocator(4))
                ax.yaxis.set_minor_locator(AutoMinorLocator(2))
                ax.tick_params(axis='y', which='major', labelsize=labelsize)
                # set minor y tick labels:
#                ax.yaxis.set_minor_formatter(FormatStrFormatter("%.2f"))
#                ax.tick_params(axis='y', which='minor', labelsize=labelsize-8)
                ax.yaxis.tick_left()
                if j == 0:
                    if kind != 'hist':
                        ax.set_ylabel(scope_dict[scope]['ylabel'], fontsize=16)
                    else:
                        ax.set_ylabel('Frequency', fontsize=16)
#                elif j == 1:
#                    if i>5:
#                        ax.set_ylabel(scope_dict[scope]['ylabel'], fontsize=12)
                site_label = '{} ({:.0f})'.format(site.upper(), geo.loc[site].alt)
                ax.text(.17, .87, site_label, fontsize=fontsize,
                        horizontalalignment='center', fontweight='bold',
                        transform=ax.transAxes)
#                ax.yaxis.grid(
#                    True,
#                    which='minor',
#                    linestyle='--',
#                    linewidth=1,
#                    alpha=0.7)
#                ax.yaxis.grid(True, linestyle='--', linewidth=1, alpha=0.7)
                if ylim is not None:
                    ax.set_ylim(*ylim)
#            except KeyError:
#                ax.set_axis_off()
#    for i, ax in enumerate(fg.axes[:, 0]):
#        try:
#            df[gr1].iloc[:, i].plot(ax=ax)
#        except IndexError:
#            ax.set_axis_off()
#    for i, ax in enumerate(fg.axes[:, 1]):
#        try:
#            df[gr2].iloc[:, i].plot(ax=ax)
#        except IndexError:
#            ax.set_axis_off()
#    for i, ax in enumerate(fg.axes[:, 2]):
#        try:
#            df[gr3].iloc[:, i].plot(ax=ax)
#        except IndexError:
#            ax.set_axis_off()

    fg.fig.tight_layout()
    fg.fig.subplots_adjust()
    if save:
        filename = 'pw_{}_means_{}.png'.format(scope, kind)
        plt.savefig(savefig_path / filename, orientation='portrait')
#        plt.savefig(savefig_path / filename, orientation='landscape')
    return fg


def prepare_diurnal_variability_table(path=work_yuval, rename_cols=True):
    from PW_stations import calculate_diurnal_variability
    df = calculate_diurnal_variability()
    gr = group_sites_to_xarray(scope='diurnal')
    gr_df = gr.to_dataframe('sites')
    new = gr.T.values.ravel()
    geo = [gr_df[gr_df == x].dropna().index.values.item()[1] for x in new]
    geo = [x.title() for x in geo]
    df = df.reindex(new)
    if rename_cols:
        df.columns = ['Annual [%]', 'JJA [%]', 'SON [%]', 'DJF [%]', 'MAM [%]']
    cols = [x for x in df.columns]
    df['Location'] = geo
    cols = ['Location'] + cols
    df = df[cols]
    df.index = df.index.str.upper()
    print(df.to_latex())
    print('')
    print(df.groupby('Location').mean().to_latex())
    return df


def prepare_harmonics_table(path=work_yuval, season='ALL'):
    import xarray as xr
    from aux_gps import run_MLR_diurnal_harmonics
    import pandas as pd
    ds = xr.load_dataset(work_yuval / 'GNSS_PW_harmonics_diurnal.nc')
    stations = list(set([x.split('_')[0] for x in ds]))
    records = []
    for station in stations:
        diu_ph = ds[station + '_mean'].sel(season=season, cpd=1).argmax()
        diu_amp = ds[station + '_mean'].sel(season=season, cpd=1).max()
        semidiu_ph = ds[station + '_mean'].sel(season=season, cpd=2, hour=slice(0, 12)).argmax()
        semidiu_amp = ds[station + '_mean'].sel(season=season, cpd=2, hour=slice(0, 12)).max()
        ds_for_MLR = ds[['{}'.format(station), '{}_mean'.format(station)]]
        harm_di = run_MLR_diurnal_harmonics(ds_for_MLR, season=season, plot=False)
        record = [station, diu_amp.item(), diu_ph.item(), harm_di[1],
                  semidiu_amp.item(), semidiu_ph.item(), harm_di[2],
                  harm_di[1] + harm_di[2]]
        records.append(record)
    df = pd.DataFrame(records)
    df.columns = ['Station', 'A1 [mm]', 'P1 [UTC]', 'V1 [%]', 'A2 [mm]',
                  'P2 [UTC]', 'V2 [%]', 'VT [%]']
    df = df.set_index('Station')
    gr = group_sites_to_xarray(scope='diurnal')
    gr_df = gr.to_dataframe('sites')
    new = gr.T.values.ravel()
    geo = [gr_df[gr_df == x].dropna().index.values.item()[1] for x in new]
    geo = [x.title() for x in geo]
    df = df.reindex(new)
    df['Location'] = geo
    df.index = df.index.str.upper()
    pd.options.display.float_format = '{:.1f}'.format
    df = df[['Location', 'A1 [mm]', 'A2 [mm]', 'P1 [UTC]', 'P2 [UTC]', 'V1 [%]', 'V2 [%]', 'VT [%]']]
    print(df.to_latex())
    return df


def plot_october_2015(path=work_yuval):
    import xarray as xr
    pw_daily = xr.load_dataset(work_yuval /
                               'GNSS_PW_daily_thresh_50_homogenized.nc')
    pw = xr.load_dataset(work_yuval / 'GNSS_PW_thresh_50_homogenized.nc')
    pw = pw[[x for x in pw if '_error' not in x]]
    pw_daily = pw_daily[[x for x in pw if '_error' not in x]]
    fig, ax = plt.subplots(figsize=(20,12))
    ln1 = pw['tela'].sel(time=slice('2015-07','2015-12')).plot(linewidth=0.5, ax=ax)
    ln2 = pw['jslm'].sel(time=slice('2015-07','2015-12')).plot(linewidth=0.5, ax=ax)
    ln3 = pw_daily['tela'].sel(time=slice('2015-07','2015-12')).plot(color=ln1[0].get_color(), linewidth=2.0, ax=ax)
    ln4 = pw_daily['jslm'].sel(time=slice('2015-07','2015-12')).plot(color=ln2[0].get_color(), linewidth=2.0, ax=ax)
    ax.grid()
    ax.legend(ln1+ln2+ln3+ln4, ['TELA-5mins', 'JSLM-5mins', 'TELA-daily', 'JSLM-daily'])
    fig, ax = plt.subplots(figsize=(20,12))
    ln1 = pw['tela'].sel(time='2015-10').plot(ax=ax)
    ln2 = pw['jslm'].sel(time='2015-10').plot(ax=ax)
    ax.grid()
    ax.legend(ln1+ln2, ['TELA-5mins', 'JSLM-5mins'])
    fig, ax = plt.subplots(figsize=(20,12))
    ln1 = pw['tela'].sel(time=slice('2015-10-22', '2015-10-27')).plot(ax=ax)
    ln2 = pw['jslm'].sel(time=slice('2015-10-22', '2015-10-27')).plot(ax=ax)
    ax.grid()
    ax.legend(ln1+ln2, ['TELA-5mins', 'JSLM-5mins'])
    return ax


def plot_pwv_anomalies_histogram(path=work_yuval):
    import xarray as xr
    import numpy as np
    import seaborn as sns
    from scipy.stats import norm
    pw = xr.load_dataset(
        path / 'GNSS_PW_monthly_anoms_thresh_50_homogenized.nc')
    arr = pw.to_array('station').to_dataframe('pw').values.ravel()
    arr_no_nans = arr[~np.isnan(arr)]
    mu, std = norm.fit(arr_no_nans)
    ax = sns.histplot(
        arr_no_nans,
        stat='density',
        color='tab:orange',
        alpha=0.5)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    ln = ax.plot(x, p, 'k', linewidth=2)
#    x_std = x[(x>=-std) & (x<=std)]
#    y_std = norm.pdf(x_std, mu, std)
#    x_std2 = x[(x>=-2*std) & (x<=-std) | (x>=std) & (x<=2*std)]
#    y_std2 = norm.pdf(x_std2, mu, std)
#    ax.fill_between(x_std,y_std,0, alpha=0.7, color='b')
#    ax.fill_between(x_std2,y_std2,0, alpha=0.7, color='r')
    y_std = [norm.pdf(std, mu, std), norm.pdf(-std, mu, std)]
    y_std2 = [norm.pdf(std * 2, mu, std), norm.pdf(-std * 2, mu, std)]
    ln_std = ax.vlines([-std, std], ymin=[0, 0], ymax=y_std,
                       color='tab:blue', linewidth=2)
    ln_std2 = ax.vlines([-std * 2, std * 2], ymin=[0, 0],
                        ymax=y_std2, color='tab:red', linewidth=2)
    leg_labels = ['Normal distribution fit',
                  '1-Sigma: {:.2f} mm'.format(std),
                  '2-Sigma: {:.2f} mm'.format(2 * std)]
    ax.legend([ln[0], ln_std, ln_std2], leg_labels)
    ax.set_xlabel('PWV anomalies [mm]')
    return ax

