#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)


# In[2]:


#********************************************************************************
# Import libraries
#********************************************************************************

"""
Import libraries from which to call functions. These are the R equivalent of packages
Libraries need to be installed first within the terminal using e.g. 'pip install dash'. Note that this should be
a different terminal to that displaying the jupyter notebook outputs
"""

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd  # library for data analysis which can be called as 'pd'
import numpy as np # Library for data analysis
import plotly.express as px # Library for data visualisation
import requests  # library to handle requests
import dash # Library to generate dashboard
import traceback
from jupyter_dash import JupyterDash # Library to generate dashboard
from dash import dcc # Components for generating dashboard
from dash import html # Components for generating dashboard
from dash.dependencies import Input, Output # Components for generating dashboard

"""
We can consider putting functions in a separate 'modules' script to support maintenance and reproducibility
"""


# ## Importing Data

# In[3]:


#********************************************************************************
# Import data
#********************************************************************************

# Disable scientific notation
pd.set_option('display.float_format', lambda x: '%.5f' % x)

# Set precision for dataframes (Not working)
pd.set_option('display.precision', 0)

"""
Define functions to import data sheet by sheet from the excel
Using a try block lets you test a block of code for errors or 'exceptions'
If the try block raises an error, the except block will be executed
Without the try block, there is a risk of more complex programmes crashing and errors resulting
"""

# Import data sheet for product identifier, lifespan information, mass information and source

def import_product_data(path):
    """
    :return:
    """
    try:
        # List of fields to retain from the imported file, with those not listed to be dropped
        fields = ['product_category_2', 
                  'PRODCOM',
                  'HS6/CN6',
                  'EoL_lower_yr',
                  'EoL_upper_yr',
                  'EoL_average_yr',
                  'Mass_lower_kg',
                  'Mass_upper_kg',
                  'Mass_average_kg',
                  'Source',
                  'Source URL']

        # Read in the data file while keeping only selected fields
        Product_data = pd.read_excel(path, sheet_name = "Lookup", usecols=fields)

        # Clear column headings of spaces and anything after brackets/parenthesis to make calling them easier
        Product_data.columns = Product_data.columns.str.replace(' ', '')
        
        # Filter to products in the product category 2 column
        Product_data = Product_data[Product_data.Source != 'Open_repair']
        
        return Product_data
    except Exception as e:
        print("Exception in import_product_data: {}".format(str(e)))
        print(traceback.format_exc())

# Import flow 

def import_flow_data(path):
    """
    :return:
    """
    try:
        # Read in the data file and sheet
        Product_flows = pd.read_excel(path, sheet_name = "Flows")
        
        # Filter to number of items in the indicator column
        filter_list_flow_indicator = ['Volume (Number of items)']
        Product_flows = Product_flows[Product_flows.Indicator.isin(filter_list_flow_indicator)]
        
        return Product_flows
    except Exception as e:
        print("Exception in import_product_data: {}".format(str(e)))
        print(traceback.format_exc())

# Import product composition data for treemap graph
        
def import_composition_data(path):
    """
    :return:
    """
    try:
        # Read in the data file
        Composition_data = pd.read_excel(path, sheet_name = "Composition")
        return Composition_data
    except Exception as e:
        print("Exception in import_product_data: {}".format(str(e)))
        print(traceback.format_exc())


# In[4]:


def import_data(path_to_file):
    """
    This functions combines the tree functions above
    :return: outputs of the above import data functions as dataframes
    """
    return import_composition_data(path_to_file), import_product_data(path_to_file), import_flow_data(path_to_file)


# In[5]:


composition_data, product_data, flow_data = import_data("../data/Product dataset.xlsx")


# Project Constants

# In[6]:


NAVBAR_OBJECTS_MARGIN = "30px"


# In[7]:


def get_products_list(product_data, flow_data):
    """
    This functions combines product data and flow data to generate a list of products.
    It takes all the unique products from product data and keeps only the ones where flow data is available
    :return: list of products
    """
    list_products = product_data["product_category_2"].unique() # Take all the unique products from product data
    list_flow = flow_data["Product"].unique() # Take all the unique products from flow data
    
    return list(set(list_products) & set(list_flow))
    


# ## Sidebar

# In[8]:


# *******************************************************************************
# Define Sidebar/Navbar
#********************************************************************************

# Defining three attributes for the navbar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# Define Sidebar Objects

# Drop down for product selection. The fixed list can be replaced with all items list
navbar_product_dropdown = dcc.Dropdown(get_products_list(product_data, flow_data), 
                                       'Laptop', 
                                       id='navbar-product-dropdown', 
                                       style={"margin-bottom": "30px"})

# Slider for lifespan selection
navbar_lifespan_slider = dcc.Slider(min=-40,
                                    max=40,
                                    step=20,
                                    value=0,
                                    id='navbar-lifespan-slider',
                                    marks={
                                        i:str(i) + "%" for i in range(-40,41,20)
                                    })

# Slider for lifespan selection
navbar_interestwindow_slider = dcc.RangeSlider(min=2010, 
                                          max=2050, 
                                          step=5, 
                                          value=[2010,2050], 
                                          id='navbar-interestwindow-slider',
                                          marks={
                                            i:"'"+str(i)[2:] for i in range(2010, 2051, 5) 
                                          })

# Adding the sidebar objects to the sidebar
sidebar = html.Div(
    [
        html.H1("CE-Hub Product Datahub", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
               html.H6("Product Selector"),
               navbar_product_dropdown,
                
               html.H6("Lifespan Input Slider"),
               navbar_lifespan_slider,
               html.Div(style={"margin-bottom": NAVBAR_OBJECTS_MARGIN}),
                
               html.H6("Window of Interest"),
               navbar_interestwindow_slider
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)


# In[22]:


# Adding the empty plot to be added in place of bar plot placeholder
margins = dict(
    l=10,
    r=10,
    b=10,
    t=10)

fig = go.Figure()

fig.update_layout(
    margin=margins,
        autosize=False,
        width=800,
        height=500)


# In[23]:


def get_eol(product):
    """
    given a product, return the lower, upper and average End of Life
    """
    data = product_data.loc[product_data["product_category_2"] == product]

    return data["EoL_lower_yr"], data["EoL_upper_yr"], data["EoL_average_yr"]


# In[59]:


def get_flow(product, var, window:list):
    """
    This functions generates the barplot from flow data and cummulative values in a given time window
    :return: Bar plot and cummulative value 
    """
    
    # Select the data from flow data only for a given product and variable (import or domestic)
    data = flow_data.loc[(flow_data["Product"] == product) & (flow_data["Variable"] == var)]

    # Filter out years depending on the time window
    years = data.columns[3:] # discard the first 3 columns as only the one's after that contain the relevant information
    y_all = data[years] # calculate the cummulative sum
    years = [year for year in years if year >= window[0] and year <= window[1]] # filter out the years according to the window
    
    
    # Define the plots
    if years == []:
        return go.Figure(), "NaN" # return an empty figure if the window doesn't contain any data points.
    
    # Plot only for the years of data defined in the window
    y_filtered = y_all[years].values[0] # get only the values for the years in the window. The cummulative sum still starts at the first year (2010)
    flow_fig = go.Figure(data=go.Bar(
        x=years,
        y= (y_filtered/1000000).round(1)
    ))
    
    # Update the layout according to the requirements
    flow_fig.update_layout(
        title="Number of goods imported by year",
        yaxis_title="Number of Items imported (in Millions)",
        xaxis_title="Year",
        autosize=False,
        width=800,
        height=500,
    )

    return flow_fig, [html.P("Cummulated Number of products: ") , html.Strong(str(round(sum(y_filtered)/1000000, 1))), html.Strong('M '), f"as of {max(years)}"]


# In[60]:


def get_treemap(product):
    """
    buillds a treemap out of the composition data given the product name (e.g. 'Laptop')
    :return: The treemap plotly object
    """
    
    # Filtering the composition data for selected product from dropdown
    data = composition_data.loc[composition_data["Product"] == product] 
    data["Percentage"] = data["Percentage"]*100 # Multiplies the percentage value by 100 to compensate for the % symbol after values in the excel sheet
    
    # Defining the treemap to be generated from the data filtered above for the selected product
    tree_fig = px.treemap(
        data_frame=data, # The filtered data
        parents="Product", # The parent at which level the tree data has to be considered
        names="Material", # Name of the blocks in the treemap
        values="Percentage", # The values on whose basis the size of the box will be decided
        title="Product composition", # The title of the treemap
        )
    
    tree_fig.data[0].hovertemplate = '%{label}<br>%{value}%'
    
    # Updating the layout of the plot to make it fit within requirements
    tree_fig.update_layout(
        margin=margins,
        autosize=False,
        width=800,
        height=300,
    )
    
    return tree_fig


# ## Main App

# In[61]:


#********************************************************************************
# Defining the Layout of the application
#********************************************************************************

layout = html.Div([
    
    dbc.Row([
        
        # Adding the sidebar/navbar
        dbc.Col([sidebar], width=2),
        
        # The section for Tree plot and the EoL values
        dbc.Col([
        
            dbc.Row([
                
                # Adding tree plot
                dbc.Col([
                    dcc.Graph(
                        id="tree-fig",
                        figure=None),
                ], width=6, style={"border-right":"1px black solid"}),
                
                
                # Adding three EoL values below
                dbc.Col([
                    dbc.Alert(html.H3(id="eol-lower", style={"textAlign":"center"})),
                ], width=2),

                dbc.Col([
                    dbc.Alert(html.H3(id="eol-upper", style={"textAlign":"center"})),
                ], width=2),
                
                dbc.Col([
                    dbc.Alert(html.H3(id="eol-average", style={"textAlign":"center"})),
                ], width=2),

            ], align="center"),
            
            html.Div( style={"border":"1px black solid"}),
            
            # This section is to add the 3 bar plots and three boxes for their cummulative values
            dbc.Row([
                dbc.Col([

                    dbc.Row([
                        # The first plot and its cummulative value
                        dbc.Col([
                            dcc.Graph(
                                id="imports-fig",
                                figure=None)
                        ], width=5),
                        dbc.Col([
                            dbc.Alert(
                                html.H3(
                                id="imports-sum",
                                style={"textAlign":"center"})
                                )
                        ], width=4)

                    ], align="center"),
                    dbc.Row([
                        #Second plot and respective value
                        dbc.Col([
                            dcc.Graph(figure=fig)
                        ], width=5),
                        dbc.Col([
                            html.P(
                                children="val"
                                ),
                        ], width=4)

                    ], align="center"),
                    
                    dbc.Row([
                        #Third row and it's respective value
                        dbc.Col([
                            dcc.Graph(figure=fig)
                        ], width=5),
                        dbc.Col([
                            html.P("val"),
                        ], width=4)

                    ], align="center")
                ])
            ])

    ], width=10)
    ])
])


# In[62]:


# *******************************************************************************
# Application Execution
#********************************************************************************

# Define the applicartoin and theme
app = JupyterDash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = layout # Add layout to the app


# Callback for interactively updating the charts and values
@app.callback(
    Output("eol-lower", "children"), # For the EoL Lower value
    Output("eol-upper", "children"), # For the EoL Upper value
    Output("eol-average", "children"), # For the EoL Average value
    Output("imports-sum", "children"), # For the cummulative sum box
    Output("tree-fig", "figure"), # For the tree plot
    Output("imports-fig", "figure"), # For the empty plots
    Input('navbar-product-dropdown', "value"), # For product dropdown slider
    Input('navbar-interestwindow-slider', "value") # For Interest of window slider
    #Input('navbar-lifespan-slider', "value"), # This can be activated when necessary
)



def update_display(product_selected, window_selected):
    
    """
    Based on the callbacks set above, this functions returns updated values when
    interaction happens on the dashboard
    """


    eols = [str(i.values[0]) for i in get_eol(product_selected)] # Extract the selected product

    fig, total = get_flow(product_selected, "Imports", window_selected) # Get the flow chart for the product selected above
    
    # The returns all objects for new selected product or changed window of interested
    return (
        "EoL lower: " + str(eols[0]), # EoL Upper value
        "EoL upper: " + str(eols[1]), # EoL Lower value
        "EoL average: " + str(eols[2]), # EoL average value
        total, # Sum of the bar plot
        get_treemap(product_selected), # Treemap for composition
        fig # The bar plot
    )


app.run_server(mode='external', port = 8050, dev_tools_ui=True, #debug=True,
              dev_tools_hot_reload =True, threaded=True)


# In[ ]:





# In[ ]:





# In[ ]:




