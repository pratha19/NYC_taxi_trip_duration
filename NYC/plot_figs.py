"""
This module contains user defined functions to plot figures used in the EDA notebook.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
plt.style.use('bmh')
plt.rcParams['figure.figsize'] = [10, 5]
import bokeh, bokeh.plotting, bokeh.models
from bokeh.io import output_notebook, show
import geopandas as gpd
from shapely.geometry import Point
import numpy as np


def plot_points(df, colA = 'pickup_longitude', colB = 'pickup_latitude', s = 0.5, alpha = 0.5, 
                color_points = 'xkcd:lime', color_background = 'xkcd:black', figsize = (7,7),
                nyc_long_limits = (-74.257159, -73.699215), nyc_lat_limits = (40.471021, 40.987326)):
   
    """
    PLotting the lat and lon of the pickup locations to get a gist of the data.
    The nyc_long_limits and nyc_lat_limits constraint the plot to the NYC boundaries.
    """
    nyc_long_limits = nyc_long_limits
    nyc_lat_limits = nyc_lat_limits
    # Scaling the figure size so that the figure scales up as per the lat and lon differences
    figsize = (abs(nyc_long_limits[0] - nyc_long_limits[1])*figsize[0], 
                            abs(nyc_lat_limits[0] - nyc_lat_limits[1])*figsize[1])
    
    fig, ax = plt.subplots(1, figsize = figsize)
    _ = ax.scatter(df[colA].values, df[colB].values,
                  color = color_points, s = s, label='train', alpha = alpha)
    
    _ = ax.set_ylabel('latitude')
    _ = ax.set_xlabel('longitude')
    
    _ = plt.ylim(nyc_lat_limits)
    _ = plt.xlim(nyc_long_limits)
    _ = plt.title(colA.replace("_", " ").split(" ")[0] + ' locations')
    
    _ = ax.set_facecolor(color_background)
    _ = ax.grid(False)    #= plt.grid(b=None)
    
def distribution(x_col, data, scale = None, bins = 100, figsize = (10,7)):
    """ Function for plotting histogram of any particular x variable of a dataframe
    """
    _ = sns.set(rc={'figure.figsize':figsize})
    _ = sns.distplot(data[x_col], bins = bins, kde=False)
    _ = plt.title('Distribution of \'{}\''.format(x_col.capitalize().replace('_', ' ')))
    _ = plt.xlabel(x_col.capitalize().replace('_', ' '))
    _ = plt.ylabel('count')
    if scale: 
        _ = plt.xscale(scale)
        
def zone_plot(nyc_shp, fill_color = 'LocationID'):
    gjds = bokeh.models.GeoJSONDataSource(geojson = nyc_shp.to_json())
    TOOLS = "pan, wheel_zoom,reset,hover,save"
    
    plot_zone = bokeh.plotting.figure(title = "NYC Taxi Zones", tools = TOOLS,
        x_axis_location = None, y_axis_location = None)#, responsive=True)
    
    color_mapper = bokeh.models.LinearColorMapper(palette = bokeh.palettes.Viridis256)
    
    plot_zone.patches('xs', 'ys', 
              fill_color = {'field': fill_color, 'transform': color_mapper},#borough_num
              fill_alpha = 1., line_color="black", line_width = 0.5,          
              source = gjds)
    
    plot_zone.grid.grid_line_color = None
    
    hover = plot_zone.select_one(bokeh.models.HoverTool)
    hover.point_policy = "follow_mouse"
    
    hover.tooltips = [
                        ("Name", "@zone"),
                        ("Borough", "@borough"),
                        ("Zone ID", "@LocationID"),
                        ("(Lon, Lat)", "($x ˚E, $y ˚N)")
                         ]
    return(plot_zone)

def assign_taxi_zones(df, lon_var, lat_var, locid_var):
    
    # make a copy since we will modify lats and lons
    localdf = df[[lon_var, lat_var]].copy()
    
    # missing lat lon info is indicated by nan. Fill with zero
    # which is outside New York shapefile. 
    localdf[lon_var] = localdf[lon_var].fillna(value=0.)
    localdf[lat_var] = localdf[lat_var].fillna(value=0.)
    

    shape_df = gpd.read_file('../data/external/taxi_zones_shape/taxi_zones.shp')
    shape_df.drop(['OBJECTID', "Shape_Area", "Shape_Leng"],
                   axis=1, inplace=True)
    shape_df = shape_df.to_crs({'init': 'epsg:4326'})

    try:
        local_gdf = gpd.GeoDataFrame(
            localdf, crs={'init': 'epsg:4326'},
            geometry=[Point(xy) for xy in
                      zip(localdf[lon_var], localdf[lat_var])])

        local_gdf = gpd.sjoin(
            local_gdf, shape_df, how='left', op='within')

        return local_gdf.LocationID.rename(locid_var)
    except ValueError as ve:
        print(ve)
        print(ve.stacktrace())
        series = localdf[lon_var]
        series = np.nan
        return series