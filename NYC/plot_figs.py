"""
This module contains user defined functions to plot figures used in the EDA notebook.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
plt.style.use('bmh')
plt.rcParams['figure.figsize'] = [10, 5]
import geopandas as gpd
from shapely.geometry import Point
import bokeh_catplot
import numpy as np
from bokeh.io import output_file, output_notebook, show, curdoc
import bokeh, bokeh.plotting, bokeh.models # check if repeated
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, LogColorMapper, BasicTicker, LogTicker, ColorBar,
    DataRange1d, Range1d, PanTool, WheelZoomTool, BoxSelectTool, ResetTool, SaveTool, CustomJS, Slider,
    Legend, LegendItem
                            )
from bokeh.models.widgets import Button, CheckboxButtonGroup, CheckboxGroup
from bokeh.models.mappers import ColorMapper, LinearColorMapper, CategoricalColorMapper
from bokeh import palettes
from bokeh.layouts import column, row, widgetbox, gridplot
from bokeh.plotting import figure, gmap, show
#output_notebook()

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

def bokeh_distplot(data, category_col = 'trip_bins_minutes', value = 'pickup_latitude',
                  plot_width=500, plot_height = 300):
    """
    Plots the distribution of the _value_ varaible categorized by the _category_col_.
    """
    p = bokeh_catplot.histogram(
    data = data,
    cats = category_col,
    val = value, plot_width = plot_width, plot_height = plot_height, 
    title = "Distribution of "+value+" categorized by "+category_col
                                )
    return(p)
        
def zone_plot(nyc_shp, fill_color = 'LocationID'):
    """
    Plots the zone and borough boundaries.
    """
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
    


def plot_single_gmaps(data, latitude_column = 'pickup_latitude', longitude_column = 'pickup_longitude', 
                         color_column = 'trip_duration', size_column = 0.5,
                         api_key = None, map_type = 'roadmap', map_zoom = 10):
    
    """
    Plot interactive plot of all data points on a google map.
    Takes in the columns of data including the lat and lon to be plotted on gmaps. 
    data: dataframe including the lat and lon locations
    color_column: column name according to which the points will be colored and a colorbar will be plotted
    size_column: can be int/float or column name in string. If column name then that column will be used to scale the size of the points.
    api_key: your google maps api key
    """
    data = data.copy()
    if not isinstance(size_column, str):
        s = size_column
        size_column = 'constant'
        data[size_column] = s
        
    map_options = GMapOptions(lat = data[latitude_column].mean(), lng = data[longitude_column].mean(), 
                              map_type = map_type, zoom = map_zoom)
    
    Tools = "box_select, wheel_zoom, pan, reset, help" 
    
    # You can use either a GmapPlot or gmap to create the plot
    plot = GMapPlot(api_key = api_key, map_options = map_options, #x_range = Range1d(), y_range = Range1d(),
                    plot_width = 500, plot_height = 400, )  #google_, gmap, tools = Tools
    
    pan = PanTool()
    wheel_zoom = WheelZoomTool()
    box_select = BoxSelectTool() 
    reset_tool = ResetTool() 
    save_tool = SaveTool()
    
    plot.add_tools(pan, wheel_zoom, box_select, reset_tool, save_tool)
    
    plot.title.text = "NYC taxi {} locations {}".format(latitude_column.split('_')[0].capitalize(), 
                                                        data.pickup_datetime.dt.year.unique().tolist())
    
    #plot.api_key = api_key
    
    source = ColumnDataSource(
        data = dict(
            lat = data[latitude_column].tolist(),
            lon = data[longitude_column].tolist(),
            size = data[size_column].tolist(),
            color = data[color_column].tolist()
        )
    )
    
    #color_mapper = LinearColorMapper(palette="Dark2")

    if not np.issubdtype(data[color_column].dtype, np.number):
        raise TypeError('Only numeric data types can be passed as a color column')
    else:
        color_mapper = LinearColorMapper(palette = "RdYlBu5", low = np.percentile(data[color_column], 1), 
                                                              high = np.percentile(data[color_column], 99)) #bokeh.palettes.Turbo256
        color_bar = ColorBar(color_mapper = color_mapper, ticker = BasicTicker(),
                            label_standoff = 12, border_line_color = None, location = (0,0), title = color_column)
        plot.add_layout(color_bar, 'right')
    circle = Circle(x = "lon", y = "lat", fill_alpha = 0.7, size = "size", 
                    fill_color  ={'field': 'color', 'transform': color_mapper}, line_color = None)
    
    plot.add_glyph(source, circle)
        
    # removed the below because gmap already adds them by default. We can change it by using the tools property
    #plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), ResetTool(), SaveTool())
    
    #output_file("NYC_pickup_plot.html")
    #output_notebook()
    return(plot, output_file("gmap.html"))


def plot_zone_trips_counts(df, nyc_shp, to_plot = 'count', col_to_plot = "pickup_taxizone_id"):
    
    """ Plots the total number of rides or the average trip duration within all zones in NYC. 
        df: dataframe
        nyc_shp: shape file
        to_plot: 'count' or 'trip_duration'
        col_to_plot: pickup_taxizone_id or dropoff_taxizone_id
    """
    
    df = df.copy()
    if to_plot == 'count':
        counts = df.groupby(col_to_plot).size().reset_index(name='N')
        tag = "Number of trips"
        ticker = LogTicker()
        cbar_title = "Total number of "+col_to_plot.split("_")[0]+"s "
        color_mapper = bokeh.models.LogColorMapper(palette = bokeh.palettes.Turbo256, low = 1, high = counts.N.max())

    elif to_plot == 'trip_duration':
        counts = df.groupby(col_to_plot)['trip_duration'].mean().reset_index(name='N')
        counts['N'] = counts['N']/60
        tag = "Trip duration mts"
        ticker = BasicTicker()#LogTicker()
        cbar_title = "Trip duration in minutes"
        color_mapper = bokeh.models.LinearColorMapper(palette = bokeh.palettes.Turbo256, low = 1, high = counts.N.max())
        
    counts2 = nyc_shp.merge(counts, left_on='LocationID', 
                            #right_index=True, 
                            right_on = col_to_plot,
                            how='left')
    
    gjds = bokeh.models.GeoJSONDataSource(geojson = counts2.to_json())
    TOOLS = "pan,wheel_zoom,reset,hover,save"
    title = "NYC Taxi "+col_to_plot.split("_")[0]+"s " + to_plot + " map"
    p = bokeh.plotting.figure(title = title, tools = TOOLS,
                              x_axis_location = None, y_axis_location = None,) 
                              #plot_width = np.int(1.08*500), plot_height = 500)
    
    p.patches('xs', 'ys', 
              fill_color = {'field': 'N', 'transform': color_mapper},
              fill_alpha = 1., line_color = "black", line_width=0.5,          
              source = gjds)
    
    p.grid.grid_line_color = None
    
    hover = p.select_one(bokeh.models.HoverTool)
    hover.point_policy = "follow_mouse"
   
    hover.tooltips = [
                        ("Name", "@zone"),
                        ("Borough", "@borough"),
                        (tag, "@N"),
                        ("Zone ID", "@LocationID")
                     ]


    color_bar = bokeh.models.ColorBar(
                                    color_mapper = color_mapper, orientation='horizontal',
                                    ticker = ticker,
                                    formatter=bokeh.models.PrintfTickFormatter(format = '%d'),
                                    label_standoff = 12, border_line_color = None, 
                                    location = (0,0), title = cbar_title)
    
    p.add_layout(color_bar, 'below')
    
    return p
