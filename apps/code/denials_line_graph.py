# %%
# Import libraries - organized by functionality
# Core data manipulation
import os
import pandas as pd
import numpy as np
import json  # Add this to the first cell with other imports

# Visualization
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc
from plotly.colors import sample_colorscale, qualitative
from plotly.subplots import make_subplots

# Dashboard
import dash
from dash import Dash, dcc, html, Input, Output, callback, callback_context, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import ALL, MATCH

# System utilities
import signal
import subprocess
import requests
import io

# %%

DATA_URL = os.environ["DATA_URL"]

r = requests.get(DATA_URL)
df = pd.read_parquet(io.BytesIO(r.content))

df = df.rename(columns={'betos_label': 'betos_category'})

# %%
# Rename "No RBCS Family" to "Other" when a subcategory has both named families and "No RBCS Family"
def rename_no_rbcs_to_other(df):
    """
    Rename 'No RBCS Family' to 'Other' only when a subcategory has both 
    'No RBCS Family' and other named families.
    """
    df_copy = df.copy()
    
    # Find subcategories that have "No RBCS Family"
    subcats_with_no_rbcs = df_copy[df_copy['betos_family'] == 'No RBCS Family']['betos_subcategory'].unique()
    
    # For each subcategory, check if it has other families besides "No RBCS Family"
    for subcat in subcats_with_no_rbcs:
        families_in_subcat = df_copy[df_copy['betos_subcategory'] == subcat]['betos_family'].unique()
        
        # If the subcategory has more than just "No RBCS Family", rename it to "Other"
        if len(families_in_subcat) > 1:
            mask = (df_copy['betos_subcategory'] == subcat) & (df_copy['betos_family'] == 'No RBCS Family')
            df_copy.loc[mask, 'betos_family'] = 'Other'
    
    return df_copy

# Apply the renaming function
df = rename_no_rbcs_to_other(df)

# %%
# Utility functions for computing metrics from pre-aggregated summary
def get_rate_df(df, group_cols):
    """Compute final denial rates from pre-aggregated data (denied==1 and paid==0)"""
    total = df.groupby(group_cols + ['year']).agg(total_claims=('total_claims', 'sum')).reset_index()
    # Final denial = denied==1 and paid==0 (denied claims that were not eventually paid)
    final_denied = df[(df.denied == 1) & (df.paid == 0)].groupby(group_cols + ['year']).agg(denied_claims=('total_claims', 'sum')).reset_index()
    merged = total.merge(final_denied, on=group_cols + ['year'], how='left').fillna({'denied_claims': 0})
    merged['denial_rate'] = merged['denied_claims'] / merged['total_claims'] * 100
    return merged

def get_initial_denial_rate_df(df, group_cols):
    """Compute initial denial rates from pre-aggregated data (denied==1 regardless of payment)"""
    total = df.groupby(group_cols + ['year']).agg(total_claims=('total_claims', 'sum')).reset_index()
    # Initial denial = denied==1 (all denials, regardless of eventual payment)
    initial_denied = df[df.denied == 1].groupby(group_cols + ['year']).agg(denied_claims=('total_claims', 'sum')).reset_index()
    merged = total.merge(initial_denied, on=group_cols + ['year'], how='left').fillna({'denied_claims': 0})
    merged['denial_rate'] = merged['denied_claims'] / merged['total_claims'] * 100
    return merged

def get_appeal_rate_df(df, group_cols):
    """Compute appeal rate from pre-aggregated data"""
    total = df.groupby(group_cols + ['year']).agg(total_claims=('total_claims', 'sum')).reset_index()
    appealed = df[df.appealed == 1].groupby(group_cols + ['year']).agg(appealed_claims=('total_claims', 'sum')).reset_index()
    merged = total.merge(appealed, on=group_cols + ['year'], how='left').fillna({'appealed_claims': 0})
    merged['appeal_rate'] = merged['appealed_claims'] / merged['total_claims'] * 100
    return merged

def get_appeal_approval_rate_df(df, group_cols):
    """Compute appeal approval rate from pre-aggregated data"""
    appeal_df = df[df.appealed == 1]
    total = appeal_df.groupby(group_cols + ['year']).agg(total_appeals=('total_claims', 'sum')).reset_index()
    approved = appeal_df[appeal_df.paid == 1].groupby(group_cols + ['year']).agg(approved=('total_claims', 'sum')).reset_index()
    merged = total.merge(approved, on=group_cols + ['year'], how='left').fillna({'approved': 0})
    merged['appeal_approval_rate'] = merged['approved'] / merged['total_appeals'] * 100
    return merged

def get_spending_df(df, group_cols, per_member=False):
    """Compute spending from pre-aggregated data"""
    sp = df.groupby(group_cols + ['year']).agg(
        total_spending=('total_spending', 'sum'), 
        unique_benes=('unique_benes', 'first')
    ).reset_index()
    if per_member:
        sp['per_member_spending'] = sp['total_spending'] / sp['unique_benes']
    return sp

# %%
# ----- DATA PREPARATION -----
# Define hierarchy levels
levels = [
    ('level1', ['betos_category']),
    ('level2', ['betos_category', 'betos_subcategory']),
    ('level3', ['betos_category', 'betos_subcategory', 'betos_family'])
]

# Compute dataframes for each metric and level
rate_dfs_final, rate_dfs_initial, appeal_rate_dfs, appeal_approval_rate_dfs, spending_dfs, per_member_spending_dfs = ({}, {}, {}, {}, {}, {})
for lvl, cols in levels:
    rate_dfs_final[lvl] = get_rate_df(df, cols)  # Final denials (denied==1 and paid==0)
    rate_dfs_initial[lvl] = get_initial_denial_rate_df(df, cols)  # Initial denials (denied==1)
    appeal_rate_dfs[lvl] = get_appeal_rate_df(df, cols)
    appeal_approval_rate_dfs[lvl] = get_appeal_approval_rate_df(df, cols)
    spending_dfs[lvl] = get_spending_df(df, cols, per_member=False)
    per_member_spending_dfs[lvl] = get_spending_df(df, cols, per_member=True)

# Compute total metrics across levels
rate_total_final = {
    'overall': get_rate_df(df, []),  # Final denials
    'by_category': get_rate_df(df, ['betos_category']),
    'by_subcategory': get_rate_df(df, ['betos_category', 'betos_subcategory'])
}
rate_total_initial = {
    'overall': get_initial_denial_rate_df(df, []),  # Initial denials
    'by_category': get_initial_denial_rate_df(df, ['betos_category']),
    'by_subcategory': get_initial_denial_rate_df(df, ['betos_category', 'betos_subcategory'])
}
appeal_rate_total = {
    'overall': get_appeal_rate_df(df, []),
    'by_category': get_appeal_rate_df(df, ['betos_category']),
    'by_subcategory': get_appeal_rate_df(df, ['betos_category', 'betos_subcategory'])
}
appeal_approval_rate_total = {
    'overall': get_appeal_approval_rate_df(df, []),
    'by_category': get_appeal_approval_rate_df(df, ['betos_category']),
    'by_subcategory': get_appeal_approval_rate_df(df, ['betos_category', 'betos_subcategory'])
}
spending_total = {
    'overall': get_spending_df(df, [], per_member=False),
    'by_category': get_spending_df(df, ['betos_category'], per_member=False),
    'by_subcategory': get_spending_df(df, ['betos_category', 'betos_subcategory'], per_member=False)
}
per_member_spending_total = {
    'overall': get_spending_df(df, [], per_member=True),
    'by_category': get_spending_df(df, ['betos_category'], per_member=True),
    'by_subcategory': get_spending_df(df, ['betos_category', 'betos_subcategory'], per_member=True)
}

# Unpack datasets for plotting callbacks
rate_df_level1_final, rate_df_level2_final, rate_df_level3_final = [rate_dfs_final[l] for l, _ in levels]
rate_df_level1_initial, rate_df_level2_initial, rate_df_level3_initial = [rate_dfs_initial[l] for l, _ in levels]
appeal_rate_df_level1, appeal_rate_df_level2, appeal_rate_df_level3 = [appeal_rate_dfs[l] for l, _ in levels]
appeal_approval_rate_df_level1, appeal_approval_rate_df_level2, appeal_approval_rate_df_level3 = [appeal_approval_rate_dfs[l] for l, _ in levels]
spending_df_level1, spending_df_level2, spending_df_level3 = [spending_dfs[l] for l, _ in levels]
per_member_spending_df_level1, per_member_spending_df_level2, per_member_spending_df_level3 = [per_member_spending_dfs[l] for l, _ in levels]

rate_df_total_overall_final = rate_total_final['overall']
rate_df_total_by_category_final = rate_total_final['by_category']
rate_df_total_by_subcategory_final = rate_total_final['by_subcategory']
rate_df_total_overall_initial = rate_total_initial['overall']
rate_df_total_by_category_initial = rate_total_initial['by_category']
rate_df_total_by_subcategory_initial = rate_total_initial['by_subcategory']

appeal_rate_df_total_overall = appeal_rate_total['overall']
appeal_rate_df_total_by_category = appeal_rate_total['by_category']
appeal_rate_df_total_by_subcategory = appeal_rate_total['by_subcategory']
appeal_approval_rate_df_total_overall = appeal_approval_rate_total['overall']
appeal_approval_rate_df_total_by_category = appeal_approval_rate_total['by_category']
appeal_approval_rate_df_total_by_subcategory = appeal_approval_rate_total['by_subcategory']

spending_df_total_overall = spending_total['overall']
spending_df_total_by_category = spending_total['by_category']
spending_df_total_by_subcategory = spending_total['by_subcategory']
per_member_spending_df_total_overall = per_member_spending_total['overall']
per_member_spending_df_total_by_category = per_member_spending_total['by_category']
per_member_spending_df_total_by_subcategory = per_member_spending_total['by_subcategory']

# ----- STYLING AND THEMING -----
# Define Urban Institute color palette for consistent styling
URBAN_COLORS = {
    'primary_blue': '#1696d2',  # Urban blue
    'black': '#000000',
    'gray': '#d2d2d2',
    'yellow': '#fdbf11',
    'magenta': '#ec008b',
    'green': '#55b748',
    'space_gray': '#5c5859',
    'red': '#db2b27'
}

# Urban color sequence for categorical data (excluding black, which is reserved for total lines)
URBAN_CATEGORICAL = [
    URBAN_COLORS['primary_blue'],
    URBAN_COLORS['yellow'],
    URBAN_COLORS['magenta'],
    URBAN_COLORS['green'],
    URBAN_COLORS['space_gray'],
    URBAN_COLORS['red'],
    URBAN_COLORS['gray']
]

# %%
# ----- DASH APP INITIALIZATION -----
# Initialize the Dash app with proper configuration
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True  # This avoids errors with dynamic callbacks
)

# ----- APP LAYOUT -----
# Define the app layout with clear organization
app.layout = dbc.Container([
    # Header section
    dbc.Row([
        dbc.Col([
            html.H1("Medicare Advantage Claim Denial Rates", className="text-center mb-4"),
        ], width=12)
    ], className="mt-4 mb-2"),
    
    # Control panel
    dbc.Row([
        # BETOS Category Dropdown
        dbc.Col([
            html.Label("BETOS Category:"),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem("All", id="cat-all", n_clicks=0),
            ] + [
                dbc.DropdownMenuItem(cat, id=f"cat-{i}", n_clicks=0) 
                for i, cat in enumerate(sorted(rate_df_level1_final.betos_category.unique()))
            ],
            label="All",
            id="category-dropdown",
            color="primary",
            className="w-100"
            ),
        ], width=12, sm=6, md=3, className="mb-2"),
        
        # BETOS Subcategory Dropdown
        dbc.Col([
            html.Label("BETOS Subcategory:"),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem("Select a category first", disabled=True)
            ],
            label="Select Category First",
            id="subcategory-dropdown", 
            color="secondary",
            className="w-100"
            ),
        ], width=12, sm=6, md=3, className="mb-2"),
        
        # Plot Metric Dropdown
        dbc.Col([
            html.Label("Lefthand Metric:"),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem("Final Denials", id="metric-final", n_clicks=0),
                dbc.DropdownMenuItem("Initial Denials", id="metric-initial", n_clicks=0),
                dbc.DropdownMenuItem("Appeal Rate", id="metric-appeal-rate", n_clicks=0),
                dbc.DropdownMenuItem("Appeal Approval Rate", id="metric-appeal-approval", n_clicks=0),
            ],
            label="Final Denials",
            id="metric-dropdown",
            color="info",
            className="w-100"
            ),
        ], width=12, sm=6, md=3, className="mb-2"),
        
        # Spending View Toggle
        dbc.Col([
            html.Label("Righthand Metric:"),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem("Total Spending", id="spending-total", n_clicks=0),
                dbc.DropdownMenuItem("Per-Member Spending", id="spending-per-member", n_clicks=0),
            ],
            label="Total Spending",
            id="spending-dropdown",
            color="success",
            className="w-100"
            ),
        ], width=12, sm=6, md=3, className="mb-2"),
    ], className="mb-4"),
    
    # Main visualization
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id='plot', 
                        style={'backgroundColor': '#ffffff', 'height': '600px'},
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': [
                                'select2d', 'lasso2d', 'resetScale2d', 'toggleSpikelines'
                            ],
                        }
                    )
                ])
            ], className="shadow")
        ], width=12)
    ], className="mb-4"),
    
    # Hidden stores for managing state
    html.Div([
        dcc.Store(id='categories-radio', data='All'),
        dcc.Store(id='subcategories-radio', data=None),
        dcc.Store(id='denial-type-toggle', data='final'),
        dcc.Store(id='spending-type-toggle', data='total'),
    ], style={'display': 'none'}),
    
    # Footer with info about the dashboard
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P(
                "BETOS Denial Analysis Dashboard - Visualizing healthcare denial rates and spending patterns",
                className="text-center text-muted small"
            ),
        ], width=12)
    ])
], fluid=True, className="px-4 py-3")

# %%
# ----- CALLBACK DEFINITIONS -----

# 1. Category dropdown callback
@callback(
    [Output('categories-radio', 'data'),
     Output('category-dropdown', 'label')],
    [Input('cat-all', 'n_clicks')] + 
    [Input(f'cat-{i}', 'n_clicks') for i in range(len(sorted(rate_df_level1_final.betos_category.unique())))],
    prevent_initial_call=True
)
def update_category(*clicks):
    """Update the selected category based on dropdown selection"""
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'cat-all':
        return 'All', 'All'
    else:
        try:
            categories = sorted(rate_df_level1_final.betos_category.unique())
            cat_index = int(button_id.split('-')[1])
            if cat_index < len(categories):
                selected_cat = categories[cat_index]
                return selected_cat, selected_cat
        except (ValueError, IndexError) as e:
            print(f"Error in category selection: {e}")
        raise PreventUpdate

# 2. Combined Subcategory Update Callback
@callback(
    [Output('subcategory-dropdown', 'children'),
     Output('subcategories-radio', 'data'),
     Output('subcategory-dropdown', 'label')],
    [Input('categories-radio', 'data'),
     Input({"type": "subcat-item", "index": ALL}, 'n_clicks')],
    [State('subcategories-radio', 'data')],
    prevent_initial_call=True
)
def update_subcategory_logic(selected_category, n_clicks_list, current_subcat_selection):
    """
    Handles all subcategory logic:
    - Populates dropdown when category changes.
    - Updates selection when a subcategory is clicked.
    """
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id_str = ctx.triggered[0]['prop_id'].split('.')[0]

    # Case 1: Category was changed
    if triggered_id_str == 'categories-radio':
        if selected_category == 'All' or not selected_category:
            return [dbc.DropdownMenuItem("Select a category first", disabled=True)], None, "Select Category First"
        
        try:
            subcategories = sorted(rate_df_level2_final[rate_df_level2_final.betos_category == selected_category].betos_subcategory.unique())
            
            menu_items = [dbc.DropdownMenuItem("All", id={"type": "subcat-item", "index": "all"}, n_clicks=0)]
            menu_items.extend([
                dbc.DropdownMenuItem(subcat, id={"type": "subcat-item", "index": i}, n_clicks=0) 
                for i, subcat in enumerate(subcategories)
            ])
            
            return menu_items, 'All', "All"
        except Exception as e:
            print(f"Error updating subcategory options: {e}")
            return [dbc.DropdownMenuItem("Error loading subcategories", disabled=True)], None, "Error"

    # Case 2: A subcategory item was clicked
    else:
        if not selected_category or selected_category == 'All' or not n_clicks_list or all(c is None for c in n_clicks_list):
            raise PreventUpdate

        try:
            prop_dict = json.loads(triggered_id_str)
            clicked_index = prop_dict.get('index')

            if clicked_index == 'all':
                return dash.no_update, 'All', 'All'
            
            subcategories = sorted(rate_df_level2_final[rate_df_level2_final.betos_category == selected_category].betos_subcategory.unique())
            if isinstance(clicked_index, int) and 0 <= clicked_index < len(subcategories):
                selected_subcat = subcategories[clicked_index]
                return dash.no_update, selected_subcat, selected_subcat
            
        except (json.JSONDecodeError, IndexError, TypeError) as e:
            print(f"Error processing subcategory selection: {e}")
            print(f"Problem property ID: {triggered_id_str}")

        # Fallback if something goes wrong
        return dash.no_update, current_subcat_selection or 'All', current_subcat_selection or 'All'

# 4. Metric dropdown callback
@callback(
    [Output('denial-type-toggle', 'data'),
     Output('metric-dropdown', 'label')],
    [Input('metric-final', 'n_clicks'),
     Input('metric-initial', 'n_clicks'),
     Input('metric-appeal-rate', 'n_clicks'),
     Input('metric-appeal-approval', 'n_clicks')],
    prevent_initial_call=True
)
def update_metric(*clicks):
    """Update the selected metric for visualization"""
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    metric_map = {
        'metric-final': ('final', 'Final Denials'),
        'metric-initial': ('initial', 'Initial Denials'),
        'metric-appeal-rate': ('appeal_rate', 'Appeal Rate'),
        'metric-appeal-approval': ('appeal_approval_rate', 'Appeal Approval Rate')
    }
    
    if button_id in metric_map:
        value, label = metric_map[button_id]
        return value, label
    
    raise PreventUpdate

# 5. Spending dropdown callback
@callback(
    [Output('spending-type-toggle', 'data'),
     Output('spending-dropdown', 'label')],
    [Input('spending-total', 'n_clicks'),
     Input('spending-per-member', 'n_clicks')],
    prevent_initial_call=True
)
def update_spending_type(*clicks):
    """Update the selected spending type for visualization"""
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'spending-total':
        return 'total', 'Total Spending'
    elif button_id == 'spending-per-member':
        return 'per_member', 'Per-Member Spending'
    
    raise PreventUpdate

# %%
# 7. Main plotting callback
@callback(
    Output('plot', 'figure'),
    [Input('categories-radio', 'data'),
     Input('subcategories-radio', 'data'),
     Input('denial-type-toggle', 'data'),
     Input('spending-type-toggle', 'data')]
)
def update_plot(selected_category, selected_subcategory, denial_type, spending_type):
    """Generate the main plot based on selections"""
    
    # Determine which datasets to use based on denial type for LEFT subplot
    if denial_type == 'final':
        level1_df = rate_df_level1_final
        level2_df = rate_df_level2_final
        level3_df = rate_df_level3_final
        total_overall = rate_df_total_overall_final
        total_by_category = rate_df_total_by_category_final
        total_by_subcategory = rate_df_total_by_subcategory_final
        y_col = 'denial_rate'
        title_prefix = 'Final Denial Rate'
        y_title = 'Final Denial Rate (%)'
    elif denial_type == 'initial':
        level1_df = rate_df_level1_initial
        level2_df = rate_df_level2_initial
        level3_df = rate_df_level3_initial
        total_overall = rate_df_total_overall_initial
        total_by_category = rate_df_total_by_category_initial
        total_by_subcategory = rate_df_total_by_subcategory_initial
        y_col = 'denial_rate'
        title_prefix = 'Initial Denial Rate'
        y_title = 'Initial Denial Rate (%)'
    elif denial_type == 'appeal_rate':
        level1_df = appeal_rate_df_level1
        level2_df = appeal_rate_df_level2
        level3_df = appeal_rate_df_level3
        total_overall = appeal_rate_df_total_overall
        total_by_category = appeal_rate_df_total_by_category
        total_by_subcategory = appeal_rate_df_total_by_subcategory
        y_col = 'appeal_rate'
        title_prefix = 'Appeal Rate'
        y_title = 'Appeal Rate (%)'
    elif denial_type == 'appeal_approval_rate':
        level1_df = appeal_approval_rate_df_level1
        level2_df = appeal_approval_rate_df_level2
        level3_df = appeal_approval_rate_df_level3
        total_overall = appeal_approval_rate_df_total_overall
        total_by_category = appeal_approval_rate_df_total_by_category
        total_by_subcategory = appeal_approval_rate_df_total_by_subcategory
        y_col = 'appeal_approval_rate'
        title_prefix = 'Appeal Approval Rate'
        y_title = 'Appeal Approval Rate (%)'
    else:
        # Default to final denial rate
        level1_df = rate_df_level1_final
        level2_df = rate_df_level2_final
        level3_df = rate_df_level3_final
        total_overall = rate_df_total_overall_final
        total_by_category = rate_df_total_by_category_final
        total_by_subcategory = rate_df_total_by_subcategory_final
        y_col = 'denial_rate'
        title_prefix = 'Final Denial Rate'
        y_title = 'Final Denial Rate (%)'
    
    # Spending data for RIGHT subplot (depends on spending_type toggle)
    if spending_type == 'per_member':
        spending_level1_df = per_member_spending_df_level1
        spending_level2_df = per_member_spending_df_level2
        spending_level3_df = per_member_spending_df_level3
        spending_total_overall = per_member_spending_df_total_overall
        spending_total_by_category = per_member_spending_df_total_by_category
        spending_total_by_subcategory = per_member_spending_df_total_by_subcategory
        spending_y_col = 'per_member_spending'
        spending_y_title = 'Per-Member Spending ($)'
        spending_subplot_title = 'Per-Member Spending'
    else:
        spending_level1_df = spending_df_level1
        spending_level2_df = spending_df_level2
        spending_level3_df = spending_df_level3
        spending_total_overall = spending_df_total_overall
        spending_total_by_category = spending_df_total_by_category
        spending_total_by_subcategory = spending_df_total_by_subcategory
        spending_y_col = 'total_spending'
        spending_y_title = 'Total Spending ($)'
        spending_subplot_title = 'Total Spending'
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f'{title_prefix}', spending_subplot_title),
        horizontal_spacing=0.15
    )
    
    # Determine what level to plot and which data to use
    if selected_category == 'All' or not selected_category:
        # Show all categories
        plot_df = level1_df
        spending_plot_df = spending_level1_df
        color_col = 'betos_category'
        
    elif not selected_subcategory or selected_subcategory == 'All':
        # Show subcategories for the selected category
        plot_df = level2_df[level2_df.betos_category == selected_category]
        spending_plot_df = spending_level2_df[spending_level2_df.betos_category == selected_category]
        color_col = 'betos_subcategory'
        
    else:
        # Show families for the selected subcategory
        plot_df = level3_df[
            (level3_df.betos_category == selected_category) & 
            (level3_df.betos_subcategory == selected_subcategory)
        ]
        spending_plot_df = spending_level3_df[
            (spending_level3_df.betos_category == selected_category) & 
            (spending_level3_df.betos_subcategory == selected_subcategory)
        ]
        color_col = 'betos_family'
    
    # Determine total data for both subplots
    if selected_category == 'All' or not selected_category:
        # Overall total across all categories
        total_data = total_overall
        spending_total_data = spending_total_overall
        total_name = 'Total (All Categories)'
    elif not selected_subcategory or selected_subcategory == 'All':
        # Total for the selected category across all subcategories
        total_data = total_by_category[total_by_category.betos_category == selected_category]
        spending_total_data = spending_total_by_category[spending_total_by_category.betos_category == selected_category]
        total_name = f'Total ({selected_category})'
    else:
        # Total for the selected subcategory across all families
        total_data = total_by_subcategory[
            (total_by_subcategory.betos_category == selected_category) & 
            (total_by_subcategory.betos_subcategory == selected_subcategory)
        ]
        spending_total_data = spending_total_by_subcategory[
            (spending_total_by_subcategory.betos_category == selected_category) & 
            (spending_total_by_subcategory.betos_subcategory == selected_subcategory)
        ]
        total_name = f'Total ({selected_subcategory})'
    
    # Add total lines first (so they appear behind other lines)
    if not total_data.empty:
        fig.add_trace(go.Scatter(
            x=total_data['year'],
            y=total_data[y_col],
            mode='lines+markers',
            name=total_name,
            line=dict(color=URBAN_COLORS['black'], width=3, dash='solid'),
            marker=dict(size=8, color=URBAN_COLORS['black']),
            hovertemplate=f'<b>{total_name}</b><br>Year: %{{x}}<br>{y_title}: %{{y:.1f}}%<extra></extra>',
            legendgroup=total_name
        ), row=1, col=1)
    
    if not spending_total_data.empty:
        # Format hover template based on spending type
        if spending_type == 'per_member':
            spending_hover = f'<b>{total_name}</b><br>Year: %{{x}}<br>{spending_y_title}: $%{{y:,.2f}}<extra></extra>'
        else:
            spending_hover = f'<b>{total_name}</b><br>Year: %{{x}}<br>{spending_y_title}: $%{{y:,.0f}}<extra></extra>'
            
        fig.add_trace(go.Scatter(
            x=spending_total_data['year'],
            y=spending_total_data[spending_y_col],
            mode='lines+markers',
            name=total_name,
            line=dict(color=URBAN_COLORS['black'], width=3, dash='solid'),
            marker=dict(size=8, color=URBAN_COLORS['black']),
            hovertemplate=spending_hover,
            showlegend=False,  # Don't show duplicate legend entry
            legendgroup=total_name
        ), row=1, col=2)

    # Add traces for each group
    if not plot_df.empty:
        unique_groups = plot_df[color_col].unique()
        
        for i, group in enumerate(unique_groups):
            group_data = plot_df[plot_df[color_col] == group]
            spending_group_data = spending_plot_df[spending_plot_df[color_col] == group]
            
            color = URBAN_CATEGORICAL[i % len(URBAN_CATEGORICAL)]
            
            # Left subplot - rates
            fig.add_trace(go.Scatter(
                x=group_data['year'],
                y=group_data[y_col],
                mode='lines+markers',
                name=group,
                line=dict(color=color, width=2),
                marker=dict(size=6),
                hovertemplate=f'<b>{group}</b><br>Year: %{{x}}<br>{y_title}: %{{y:.1f}}%<extra></extra>',
                legendgroup=group
            ), row=1, col=1)
            
            # Right subplot - spending
            if not spending_group_data.empty:
                # Format hover template based on spending type
                if spending_type == 'per_member':
                    group_spending_hover = f'<b>{group}</b><br>Year: %{{x}}<br>{spending_y_title}: $%{{y:,.2f}}<extra></extra>'
                else:
                    group_spending_hover = f'<b>{group}</b><br>Year: %{{x}}<br>{spending_y_title}: $%{{y:,.0f}}<extra></extra>'
                    
                fig.add_trace(go.Scatter(
                    x=spending_group_data['year'],
                    y=spending_group_data[spending_y_col],
                    mode='lines+markers',
                    name=group,
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
                    hovertemplate=group_spending_hover,
                    showlegend=False,  # Don't show duplicate legend entry
                    legendgroup=group
                ), row=1, col=2)
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'{title_prefix} and Total Spending by BETOS',
            x=0.5,
            font=dict(size=16, color=URBAN_COLORS['black'])
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=150, t=80, b=60),
        height=600
    )
    
    # Update x-axes
    fig.update_xaxes(
        title='Year',
        showgrid=True,
        gridcolor='lightgray',
        tickformat='d',
        row=1, col=1
    )
    fig.update_xaxes(
        title='Year',
        showgrid=True,
        gridcolor='lightgray',
        tickformat='d',
        row=1, col=2
    )
    
    # Update y-axes
    fig.update_yaxes(
        title=y_title,
        showgrid=True,
        gridcolor='lightgray',
        rangemode='tozero',  # Force y-axis to start at 0
        row=1, col=1
    )
    fig.update_yaxes(
        title=spending_y_title,
        showgrid=True,
        gridcolor='lightgray',
        row=1, col=2
    )
    
    return fig

# %%
# ----- RUN THE DASH APP -----
print("Starting the Dash app...")
print("The app will be available at: http://127.0.0.1:8052")
print("Use Ctrl+C or run the stop_dash_app() function to stop it.")

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8052))
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)

server = app.server