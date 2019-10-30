try:
    import asyncio
except ImportError:
    raise RuntimeError("This example requries Python3 / asyncio")

from flask import Flask, render_template, request, url_for, flash, session, redirect
from flask_login import LoginManager, login_user, login_required, logout_user

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from os.path import dirname, join
import geopandas as gpd
import pandas as pd
import numpy as np
import json
from shapely.geometry import Point

from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.embed import server_document
from bokeh.server.server import BaseServer
from bokeh.server.tornado import BokehTornado
from bokeh.server.util import bind_sockets
from bokeh.themes import Theme

from bokeh.io import curdoc, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, NumeralTickFormatter, ColorBar, CheckboxGroup, Text, Label, Slider, TapTool, HoverTool, ColumnDataSource
from bokeh.models.glyphs import Patches
from bokeh.layouts import WidgetBox, row, column, layout
from bokeh.palettes import d3, Category20_16
from bokeh.events import Tap


if __name__ == '__main__':
    print('This script is intended to be run with gunicorn. e.g.')
    print()
    print('    gunicorn -w 4 flask_gunicorn_embed:app')
    print()
    print('will start the app on four processes')
    import sys
    sys.exit()

from brewasisdb import get_data, add_craft, if_exist, add_salary, add_companies

app = Flask(__name__)

from securRoutes import secur
app.register_blueprint(secur)
app.secret_key = 'this should be a secret key'

from models import db, Login

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "secur.login"

@login_manager.user_loader
def load_user(user_id):
    return Login.query.filter(Login.id == int(user_id)).first()

datasets = {
      'set1': "Dataset One",
      'set2': "Dataset Two",
      'set3': "Dataset Three",
      'set4': "Dataset Four"
      }
query_craft = "select * \
                    from craft \
                    order by (barrels2018+barrels2017+barrels2016+barrels2015+barrels2014) desc"

query_state = "select state, sum(barrels2008), sum(barrels2009), sum(barrels2010) \
                    from craft \
                    group by state \
                    order by sum(barrels2010) desc"

query_brew = "select state, prod2011, prod2012, prod2013, prod2014, prod2015, prod2016, prod2017, prod2018 \
                    from brew2011_2018 \
                    order by state desc"

query_num_co = "select state, SUM (CASE WHEN (barrels2008>0) THEN 1 ELSE 0 END), SUM (CASE WHEN (barrels2009>0) THEN 1 ELSE 0 END), SUM (CASE WHEN (barrels2010>0) THEN 1 ELSE 0 END), SUM (CASE WHEN (barrels2011>0) THEN 1 ELSE 0 END), SUM (CASE WHEN (barrels2012>0) THEN 1 ELSE 0 END), SUM (CASE WHEN (barrels2013>0) THEN 1 ELSE 0 END), SUM (CASE WHEN (barrels2014>0) THEN 1 ELSE 0 END), SUM (CASE WHEN (barrels2015>0) THEN 1 ELSE 0 END), SUM (CASE WHEN (barrels2016>0) THEN 1 ELSE 0 END), SUM (CASE WHEN (barrels2017>0) THEN 1 ELSE 0 END) \
                    from craft \
                    group by state"

query_numco = "select state, num_co \
                    from brew2018 \
                    order by state desc"

query_population = "select state, pop, percent, adults \
                    from population \
                    order by state desc"

query_current = "select state, produced, population, num_co, rank, by_adults, capita \
                    from brew2018 \
                    order by state desc"

query_salary = "select size, principal, brewmaster, mngr, head, assistant, cellar, packmng, canner, other \
                     from salary \
                     order by principal"
states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
#        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

craft_temp = '''
    <table id="table_craft"> <tr> <td style = "width:200px">%s</td> <td style="width:45px">%s</td>
    <td style="width:50px">%s</td> <td style="width:50px">%s</td><td style="width:50px">%s</td> \
    <td style="width:50px">%s</td><td style="width:50px">%s</td>
    <td style="width:50px">%s</td><td style="width:50px">%s</td><td style="width:50px">%s</td> <td style="width:50px">%s</td>\
    <td style="width:50px">%s</td><td>%s</td></tr> </table>
'''

state_temp = '''
    <table id="table-state"> <tr> <td style="width:60px">%s</td>
    <td style="width:50px">%s</td> <td style="width:50px">%s</td><td style="width:50px">%s</td> \
    <td style="width:50px">%s</td><td style="width:50px">%s</td>
    <td style="width:50px">%s</td><td style="width:50px">%s</td><td style="width:50px">%s</td> \
    <td style="width:50px">%s</td><td style="width:50px">%s</td><td>%s</td></tr> </table>
'''

def dframe(query):
    state_list = get_data(query)
    for item in state_list:
        if len(item[0]) != 2:
            state_list.remove(item)
    return state_list

def modify_doc(doc):
    def callback(event):
        selected = geosource.selected.indices
        yr = slider.value
        data = get_json(str(yr), selected[0])
        sgeosource.geojson = data[0]
        text_year.text = str(yr)
        text_state.text = data[1]
        text_beer.text = str(f"{data[2]:,d}")
        text_numco.text = str(numco(data[1], str(yr)))
        text_rank.text = str(rank(data[1], str(yr)))
        text_rate.text = str(rate(data[1], str(yr)))+'%'
        text_adults.text = str(adults(data[1]))+'%'
        text_capita.text = str(capita(data[1], str(yr)))
        company_selection.labels = company(data[1])
        initial_companies = [company_selection.labels[i] for
    						i in company_selection.active]
        src.data = make_dataset(initial_companies).data

        coordinates = xysource(data[1], df1)
        ycoordinate = [i/100000 for i in coordinates[1]]
        statesource.data = dict(x=coordinates[0], y=ycoordinate)
        coordinatesplot = xysource(data[1], df4)
        numcosource.data = dict(x=coordinatesplot[0], y=coordinatesplot[1])
        splot.visible = True
        tplot.visible = True
    def xysource(state, df5):
        df2 = df5.loc[df5['states']==state]
        df2 = df2.drop('states', 1)
        list_x = [int(i) for i in list(df2)]
        list_y = df2.values[0]
        return [list_x, list_y]

    flask_args = doc.session_context.request.arguments
    try:
        plot_title = flask_args.get('plot_title')[0].decode("utf-8")
    except:
        plot_title = "Sea Surface Temperature at 43.18, -70.43"
    try:
        dataset = flask_args.get('dataset')[0].decode("utf-8")
    except:
        dataset = "Dataset One"
    try:
        unit_type = flask_args.get('unit_type')[0].decode("utf-8")
    except:
        unit_type = "Celcius"
    try:
        theme = flask_args.get('theme')[0].decode("utf-8")
    except:
        theme = "default"

    gdf = gpd.GeoDataFrame.from_file(join(dirname(__file__), 'data/states', 'gz_2010_us_040_00_20m.shp'))[['NAME', 'geometry', 'GEO_ID', 'CENSUSAREA']]

    yr = 2018
    gdf.columns = ['state', 'geometry', 'geo_id', 'censusarea']
    gdf = gdf.drop(gdf.index[26])
    gdf = gdf.drop(gdf.index[7])

    df_company = pd.DataFrame(get_data(query_craft), columns =['company','state','2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018'])
    df_companies = df_company.replace({"state": states})
    df_companies = df_companies.astype({"2008": int, "2009": int, "2010": int, "2011": int, "2012": int, "2013": int, "2014": int, "2015": int, "2016": int, "2017": int, "2018": int})


    df = pd.DataFrame(dframe(query_state), columns =['states', '2008', '2009', '2010'])
    df1 = df.replace({"states": states})
    df1 = df1.astype({"2008": int, "2009": int, "2010": int})

    df_brew = pd.DataFrame(get_data(query_brew), columns =['state', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018'])
    df_brew = df_brew.astype({"2011": int, "2012": int, "2013": int, "2014": int, "2015": int, "2016": int, "2017": int, "2018": int})

    df1 = df1.merge(df_brew, left_on = 'states', right_on = 'state')
    df1 = df1.drop('state', 1)


    df3 = pd.DataFrame(dframe(query_num_co), columns =['states', '2008', '2009', '2010', '2011','2012', '2013', '2014', '2015', '2016', '2017'])
    df4 = df3.replace({"states": states})
    df4 = df4.astype({"2008": int, "2009": int, "2010": int, "2011": int, "2012": int, "2013": int, "2014": int, "2015": int, "2016": int, "2017": int})

    df_numco = pd.DataFrame(get_data(query_numco), columns =['state', '2018'])
    df_numco = df_numco.astype({"2018": int})

    df4 = df4.merge(df_numco, left_on = 'states', right_on = 'state')
    df4 = df4.drop('state', 1)

    df_pop = pd.DataFrame(get_data(query_population), columns =['state', 'population', 'percent', 'adults'])
    df_pop = df_pop.astype({"percent": float, "adults": int})
    df_pop['percent'] = df_pop['percent']*100

    def numco(state, year):
        merged = df4.loc[df4['states'] == state]
        numco_text = merged.iloc[0][year]
        return numco_text
    def rank(state, year):
        df_rank = df4[['states', year]]
        df = df_rank.sort_values(year, ascending=False)
        df = df.reset_index(drop=True)
        idx = df.index[df['states'] == state]
        idx = idx[0]+1
        return idx
    def rate(state, year):
        rate = (100*df4.loc[df4['states'] == state][year].values[0])/df4[year].sum()
        return rate.round(2)
    def adults(state):
        adults = df_pop.loc[df_pop['state'] == state]['percent'].values[0]
        return adults.round(2)
    def capita(state, year):
        adults = df_pop.loc[df_pop['state'] == state]['adults'].values[0]
        num = numco(state, year)
        kf = 100000
        capita = (num/adults)*kf
        print (capita)
        return capita.round(1)


    def get_json(year, idx):
        df_yr = df1[['states', year]]
        df_yr.columns = ['states', 'year']
        merged = gdf.merge(df_yr, left_on = 'state', right_on = 'states')
        state_text=''
        beer_text=''

        if idx is not None:
            merged = merged.iloc[[idx]]
            state_text = merged.iloc[0]['state']
            beer_text = merged.iloc[0]['year']

        merged_json = json.loads(merged.to_json())
        json_data = json.dumps(merged_json)
        return [json_data, state_text, beer_text]
    #Input GeoJSON source that contains features for plotting.
    geosource = GeoJSONDataSource(geojson = get_json('2018', None)[0])

    #Define a sequential multi-hue color palette.
    palette = ['#084594', '#2171b5', '#4292c6', '#6baed6', '#9ecae1']
    #palette = d3['Category20b'][4]
    #Reverse color order so that dark blue is highest obesity.
    palette = palette[::-1]
    #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette = palette, low = 0, high = 2500000, nan_color = '#d9d9d9')
    #Define custom tick labels for color bar.
    tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '>40%'}
    #Add hover tool

    hover = HoverTool(tooltips = [ ('State','@state'),('brew','@year'+" bbls")], toggleable=False)
    #Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=10,width = 590, height = 20, border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
    #Create figure object.
    plot = figure(plot_width=640, plot_height=420, aspect_scale=0.85, title = 'State Craft Beer Sales 2018')
    plot.add_tools(hover)

    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.background_fill_color = "#F5F5F5"
    #Add patch renderer to figure.
    plot.axis.visible = False
    initial_map = Patches(xs='xs',ys='ys', fill_color = {'field' : 'year', 'transform' : color_mapper}, line_color = 'white', line_width = 0.15, fill_alpha = 0.5)
    selected_state = Patches(line_width = 1, fill_color= {'field' : 'year', 'transform' : color_mapper}, line_color='#00022b', fill_alpha = 0.5)
    nonselected_state = Patches(line_width = 0.15, fill_color = {'field' : 'year', 'transform' : color_mapper}, line_color='white', fill_alpha = 0.5)
    plot.add_glyph(geosource,
                initial_map,
            selection_glyph = selected_state,
            nonselection_glyph = nonselected_state)
    #Specify figure layout.
    plot.add_tools(TapTool())
    plot.on_event(Tap, callback)
    plot.add_layout(color_bar, 'below')
    splot = figure(plot_width=320, plot_height=300, match_aspect=True, title=None, toolbar_location=None)
    tplot = figure(plot_width=320, plot_height=300, title=None, toolbar_location=None, tools='')
    sales_plot = figure(plot_width=320, plot_height=300, title="Sales 2008-2018", x_axis_label = 'Year', y_axis_label = 'Barrels of Craft Beer Produced (x 100 000)', toolbar_location=None)
    numco_plot = figure(plot_width=320, plot_height=300, title="Number of Companies 2008-2018", x_axis_label = 'Year', y_axis_label = 'Number of craft beer breweries', toolbar_location=None)

    splot.axis.visible = False
    tplot.axis.visible  = False
    splot.grid.visible = False
    tplot.grid.visible = False
    splot.outline_line_width = 0
    tplot.outline_line_width = 0
#    splot.visible = False
#    tplot.visible = False

    sgeosource = GeoJSONDataSource(geojson = get_json('2018', 2)[0])
    splot.patches('xs','ys', source = sgeosource, fill_color = '#131E3A', line_color = 'black', line_width = 0.25, fill_alpha = 1)
    year_source = ColumnDataSource({'year': ['2018']})
    text_year = Label(x=250, y=250, x_units='screen', y_units='screen',text='2018',text_color='#131E3A',  text_font_size='16pt', text_font_style = 'bold')
    text_state = Label(x=0, y=250, x_units='screen', y_units='screen',text='California',text_color='#131E3A',  text_font_size='16pt', text_font_style = 'bold')
    text_beer = Label(x=145, y=220, x_units='screen', y_units='screen',text='1,032,369',text_color='#013240',  text_font_size='28pt', text_font_style = 'bold', text_font = 'Roboto', text_baseline = 'middle', text_align='right', x_offset=25)
    text_val1 = Label(x=175, y=222, x_units='screen', y_units='screen',text='Barrels of Craft Beer',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')
    text_val2 = Label(x=175, y=208, x_units='screen', y_units='screen',text='Produced per Year',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')

    text_numco = Label(x=145, y=180, x_units='screen', y_units='screen',text='750',text_color='#013240',  text_font_size='28pt', text_font_style = 'bold', text_font = 'Roboto', text_baseline = 'middle', text_align='right', x_offset=25)

    text_val3 = Label(x=175, y=182, x_units='screen', y_units='screen',text='Craft Breweries',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')
    text_val4 = Label(x=175, y=168, x_units='screen', y_units='screen',text='Operating per Year',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')

    text_rank = Label(x=145, y=140, x_units='screen', y_units='screen',text='1',text_color='#013240',  text_font_size='28pt', text_font_style = 'bold', text_font = 'Roboto', text_baseline = 'middle', text_align='right', x_offset=25)

    text_val5 = Label(x=175, y=142, x_units='screen', y_units='screen',text='Most Craft',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')
    text_val6 = Label(x=175, y=128, x_units='screen', y_units='screen',text='Breweries in the US',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')

    text_rate = Label(x=145, y=100, x_units='screen', y_units='screen',text='5%',text_color='#013240',  text_font_size='28pt', text_font_style = 'bold', text_font = 'Roboto', text_baseline = 'middle', text_align='right', x_offset=25)

    text_val7 = Label(x=175, y=102, x_units='screen', y_units='screen',text='of US Craft Breweries',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')
    text_val8 = Label(x=175, y=88, x_units='screen', y_units='screen',text='',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')

    text_adults = Label(x=145, y=60, x_units='screen', y_units='screen',text='75%',text_color='#013240',  text_font_size='28pt', text_font_style = 'bold', text_font = 'Roboto', text_baseline = 'middle', text_align='right', x_offset=25)

    text_val9 = Label(x=175, y=62, x_units='screen', y_units='screen',text='21+ Adults in state',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')
    text_val10 = Label(x=175, y=48, x_units='screen', y_units='screen',text='',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')

    text_capita = Label(x=145, y=20, x_units='screen', y_units='screen',text='2.8%',text_color='#013240',  text_font_size='28pt', text_font_style = 'bold', text_font = 'Roboto', text_baseline = 'middle', text_align='right', x_offset=25)

    text_val11 = Label(x=175, y=22, x_units='screen', y_units='screen',text='Breweries per',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')
    text_val12 = Label(x=175, y=8, x_units='screen', y_units='screen',text='100,000 21+ Adults',text_color='#013220',  text_font_size='11pt', text_font_style = 'normal', text_font = 'Roboto')


    coordinates = xysource('California', df1)
    ycoordinate = [i/100000 for i in coordinates[1]]
    statesource = ColumnDataSource(dict(x=coordinates[0],
                                       y=ycoordinate))
    coordinatesplot = xysource('California', df4)
    numcosource = ColumnDataSource(dict(x=coordinatesplot[0],
                                       y=coordinatesplot[1]))
    sales_plot.line('x', 'y', source=statesource, line_width=3, line_alpha=0.6)
    numco_plot.line('x', 'y', source=numcosource, line_width=3, line_alpha=0.6)

    tplot.add_layout(text_year)
    tplot.add_layout(text_state)
    tplot.add_layout(text_beer)
    tplot.add_layout(text_val1)
    tplot.add_layout(text_val2)
    tplot.add_layout(text_numco)
    tplot.add_layout(text_val3)
    tplot.add_layout(text_val4)
    tplot.add_layout(text_rank)
    tplot.add_layout(text_val5)
    tplot.add_layout(text_val6)
    tplot.add_layout(text_rate)
    tplot.add_layout(text_val7)
    tplot.add_layout(text_val8)
    tplot.add_layout(text_adults)
    tplot.add_layout(text_val9)
    tplot.add_layout(text_val10)
    tplot.add_layout(text_capita)
    tplot.add_layout(text_val11)
    tplot.add_layout(text_val12)


#    glyph = Text(x="x", y="y", text="text", angle=0.3, text_color="#96deb3")
#    tplot.add_glyph(source, glyph)

    def update_plot(attr, old, new):
        yr = slider.value
        new_data = get_json(str(yr), None)[0]
        geosource.geojson = new_data
        plot.title.text = 'State Craft Beer Sales, %d' %yr
    # Make a slider object: slider
    slider = Slider(title = 'Year',start = 2008, end = 2018, step = 1, value = 2018)
    slider.on_change('value', update_plot)


    def make_dataset(company_list):
        xs = []
        ys = []
        colors = []
        labels = []
#        src_circle = []
        for i, company in enumerate(company_list):
            df_co = df_companies.loc[df_companies['company']==company]
            df_co = df_co.drop(['company', 'state'], axis=1)
            list_x = [int(i) for i in list(df_co)]
            list_y = df_co.values[0]
            xs.append(list_x)
            ys.append(list_y)
            colors.append(company_colors[i])
            labels.append(company)
        new_src = ColumnDataSource(data={'x': xs, 'y': ys,
								   'color': colors, 'label': labels})
#        for i in range(0, len(new_src.data['x'])):
#            print (i)
#            src_circle.append(ColumnDataSource(data={'x': new_src.data['x'][i], 'y': new_src.data['y'][i]}))
        return new_src

    def make_plot(src):
        p = figure(plot_width = 800, plot_height = 420, title = 'Craft Beer Sales by State Companies 2008-2018', x_axis_label = 'Year', y_axis_label = 'Barrels of Craft Beer Produced, bbls')
        p.multi_line('x', 'y', color = 'color', line_alpha=0.6, hover_line_alpha=1.0, legend = 'label', line_width = 3, name='needshover', source = src)
#        for i in src_circle:
#            p.circle('x', 'y', fill_color="white", color = 'grey', size=8, source = i)
        hover = HoverTool(names=['needshover'], tooltips=[('Company', '@label'),
									('Year', '$x{int}'),
									('Barrels', '$data_y' + " bbls")]
						  )
        p.add_tools(hover)
        p.yaxis.formatter = NumeralTickFormatter(format="0.0 a")
        p.legend.location = "top_left"
        return p
    def update(attr, old, new):
        companies_to_plot = [company_selection.labels[i] for i in company_selection.active]
        new_src = make_dataset(companies_to_plot)

        src.data.update(new_src.data)


    def company(state):
        available_companies = df_companies.loc[df_companies['state'] == state][:]
        sort_companies = list(set(available_companies['company'][:20]))
        sort_companies.sort()
        return sort_companies

    company_selection = CheckboxGroup(labels=company('California'),
									   active = [0, 1])
    company_selection.on_change('active', update)
    initial_companies = [company_selection.labels[i] for
						i in company_selection.active]
    company_colors = Category20_16
    company_colors.sort()
    src = make_dataset(initial_companies)
#    src_circle = make_dataset(initial_companies)[1]
    plot_state = make_plot(src)
    controls = WidgetBox(company_selection, width = 200)
    l1 = row(controls, plot_state)

    if plot_title == '1':
        r = row([plot, tplot], sizing_mode='stretch_height')
        doc.add_root(column(r, l1))
    else:
        l = layout([[plot],[splot, tplot], [numco_plot, sales_plot]])
        doc.add_root(column(slider, l))



    doc.theme = Theme(filename=f"theme-{theme}.yaml")

bkapp = Application(FunctionHandler(modify_doc))

# This is so that if this app is run using something like "gunicorn -w 4" then
# each process will listen on its own port
sockets, port = bind_sockets("127.0.0.1", 0)
print (port)

@app.route('/', methods=['GET'])
@login_required
def bkapp_page():
    if request.args.get('title') is None:
      plot_title = "Sea Surface Temperature at 43.18, -70.43"
    else:
      plot_title = request.args.get('title')

    if plot_title == '1':
        rightdiv = 'none'
        center = 'calc(100% - 16px)'
    else:
        rightdiv  = ''
        center = ''

    if request.args.get('dataset') is None:
      current_dataset = 'set1'
    else:
      current_dataset = request.args.get('dataset')

    if request.args.get('unit_type') is None:
      unit_type = "Celcius"
    else:
      unit_type = request.args.get('unit_type')

    if request.args.get('theme') is None:
      theme = "default"
    else:
      theme = request.args.get('theme')

    script = server_document(url='http://127.0.0.1:%d/bkapp' % port,
      arguments=dict(
      plot_title = plot_title,
      dataset = datasets.get(current_dataset),
      unit_type = unit_type,
      theme = theme)
    )
    return render_template(
      "index.html",
      script = script, # Bokeh embed script for HTML rendering
      app_name = "Flask Bokeh Dashboard",
      app_description = "This Bokeh app is served by a Bokeh server embedded in Flask served with some asyncio via Gunicorn.",
      app_icon = "timeline", # To choose an icon, @see https://material.io/tools/icons/
      # We also pass parameters (back) to Flask so that our HTML form is rendered with values from request.args, if any:
      plot_title = plot_title,
      unit_type = unit_type,
      datasets = datasets,
      current_dataset = current_dataset,
      theme = theme,
      rightdiv = rightdiv,
      center = center
      )



@app.route("/craft", methods=['GET'])
@login_required
def craft_get():
    df_company = pd.DataFrame(get_data(query_craft), columns =['company','state','2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018'])
    df_companies = df_company.replace({"state": states})
    df_companies = df_companies.astype({"2008": int, "2009": int, "2010": int, "2011": int, "2012": int, "2013": int, "2014": int, "2015": int, "2016": int, "2017": int, "2018": int})
    craft_data = df_companies.to_html(index = False, classes="display compact", table_id="example")
    return render_template("craft.html", craft_data=craft_data)

@app.route("/states", methods=['GET'])
@login_required
def states_get():
    df = pd.DataFrame(dframe(query_state), columns =['states', '2008', '2009', '2010'])
    df1 = df.replace({"states": states})
    df1 = df1.astype({"2008": int, "2009": int, "2010": int})
    df1 = df1.drop(df1[df1['2008']==0].index)
    print (df1)

    df_brew = pd.DataFrame(get_data(query_brew), columns =['state', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018'])
    df_brew = df_brew.astype({"2011": int, "2012": int, "2013": int, "2014": int, "2015": int, "2016": int, "2017": int, "2018": int})

    df1 = df1.merge(df_brew, left_on = 'states', right_on = 'state')
    df1 = df1.drop('state', 1)
    state_data = df1.to_html(index = False, classes="display compact", table_id="example")
    return render_template("states.html", state_data=state_data)

@app.route("/numco", methods=['GET'])
@login_required
def numco():
    df3 = pd.DataFrame(dframe(query_num_co), columns =['states', '2008', '2009', '2010', '2011','2012', '2013', '2014', '2015', '2016', '2017'])
    df4 = df3.replace({"states": states})
    df4 = df4.astype({"2008": int, "2009": int, "2010": int, "2011": int, "2012": int, "2013": int, "2014": int, "2015": int, "2016": int, "2017": int})

    df_numco = pd.DataFrame(get_data(query_numco), columns =['state', '2018'])
    df_numco = df_numco.astype({"2018": int})

    df4 = df4.merge(df_numco, left_on = 'states', right_on = 'state')
    df4 = df4.drop('state', 1)
    numco_data = df4.to_html(index = False, classes="display compact", table_id="example")
    return render_template("numco.html", numco_data=numco_data)


@app.route("/population", methods=['GET'])
@login_required
def population():
    df_pop = pd.DataFrame(get_data(query_population), columns =['state', 'population', 'percent(21+)', 'adults(21+)'])
    df_pop = df_pop.astype({"percent(21+)": float, "adults(21+)": int})
    df_pop['percent(21+)'] = df_pop['percent(21+)']*100
    df_pop['percent(21+)'] = df_pop['percent(21+)'].round(2)
    df_pop['percent(21+)'] = df_pop['percent(21+)'].astype(str) + '%'
    pop_data = df_pop.to_html(index = False, classes="display compact", table_id="example")
    return render_template("population.html", pop_data=pop_data)

@app.route("/current", methods=['GET'])
@login_required
def current():
    df_current = pd.DataFrame(get_data(query_current), columns =['state', 'produced', 'population', 'number of breweries', 'rank by breweries', 'breweries per capita', 'capita rank'])
    current_data = df_current.to_html(index = False, classes="display compact", table_id="example")
    return render_template("current.html", current_data=current_data)

@app.route("/salary", methods=['GET'])
@login_required
def salary():
    df_salary = pd.DataFrame(get_data(query_salary), columns =['size', 'principal', 'brewmaster', 'mngr', 'head', 'assistant', 'cellar', 'packmng', 'canner', 'other'])
    print (df_salary)
    salary_data = df_salary.to_html(index = True, classes="display compact", table_id="example")
    return render_template("salary.html", salary_data=salary_data)



def bk_worker():
    asyncio.set_event_loop(asyncio.new_event_loop())

    bokeh_tornado = BokehTornado({'/bkapp': bkapp}, extra_websocket_origins=["127.0.0.1"])
    bokeh_http = HTTPServer(bokeh_tornado)
    bokeh_http.add_sockets(sockets)

    server = BaseServer(IOLoop.current(), bokeh_tornado, bokeh_http)
    server.start()
    server.io_loop.start()

from threading import Thread
Thread(target=bk_worker).start()
