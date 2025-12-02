"""
Visualization Module
Helper functions for creating charts and visualizations
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.theme_manager import update_plotly_theme


def create_line_chart(df, x, y, title, xaxis_title, yaxis_title, color=None):
    """
    Create a line chart

    Args:
        df (pd.DataFrame): Data
        x (str): X-axis column
        y (str): Y-axis column
        title (str): Chart title
        xaxis_title (str): X-axis label
        yaxis_title (str): Y-axis label
        color (str): Color column for grouping

    Returns:
        plotly figure
    """
    fig = px.line(
        df,
        x=x,
        y=y,
        title=title,
        color=color,
        markers=True
    )

    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        hovermode='x unified',
        template='plotly_white'
    )

    fig = update_plotly_theme(fig)

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def create_bar_chart(df, x, y, title, xaxis_title, yaxis_title, color=None, orientation='v'):
    """
    Create a bar chart

    Args:
        df (pd.DataFrame): Data
        x (str): X-axis column
        y (str): Y-axis column
        title (str): Chart title
        xaxis_title (str): X-axis label
        yaxis_title (str): Y-axis label
        color (str): Color column
        orientation (str): 'v' for vertical, 'h' for horizontal

    Returns:
        plotly figure
    """
    if orientation == 'h':
        fig = px.bar(
            df,
            x=y,
            y=x,
            title=title,
            color=color,
            orientation='h'
        )
        fig.update_layout(
            xaxis_title=yaxis_title,
            yaxis_title=xaxis_title
        )
    else:
        fig = px.bar(
            df,
            x=x,
            y=y,
            title=title,
            color=color
        )
        fig.update_layout(
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title
        )

    fig.update_layout(
        hovermode='x unified',
        template='plotly_white'
    )

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def create_pie_chart(values, names, title, hole=0):
    """
    Create a pie chart

    Args:
        values (list): Values
        names (list): Labels
        title (str): Chart title
        hole (float): Hole size for donut chart (0 for pie)

    Returns:
        plotly figure
    """
    fig = go.Figure(data=[go.Pie(
        labels=names,
        values=values,
        hole=hole
    )])

    fig.update_layout(
        title=title,
        template='plotly_white'
    )

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def create_scatter_plot(df, x, y, title, xaxis_title, yaxis_title, color=None, size=None):
    """
    Create a scatter plot

    Args:
        df (pd.DataFrame): Data
        x (str): X-axis column
        y (str): Y-axis column
        title (str): Chart title
        xaxis_title (str): X-axis label
        yaxis_title (str): Y-axis label
        color (str): Color column
        size (str): Size column

    Returns:
        plotly figure
    """
    fig = px.scatter(
        df,
        x=x,
        y=y,
        title=title,
        color=color,
        size=size,
        hover_data=df.columns
    )

    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        template='plotly_white'
    )

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def create_heatmap(data, x_labels, y_labels, title, colorscale='Blues'):
    """
    Create a heatmap

    Args:
        data (array): 2D array of values
        x_labels (list): X-axis labels
        y_labels (list): Y-axis labels
        title (str): Chart title
        colorscale (str): Color scale name

    Returns:
        plotly figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale=colorscale,
        text=data,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        hoverongaps=False
    ))

    fig.update_layout(
        title=title,
        template='plotly_white'
    )

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def create_box_plot(df, x, y, title, xaxis_title, yaxis_title):
    """
    Create a box plot

    Args:
        df (pd.DataFrame): Data
        x (str): X-axis column (category)
        y (str): Y-axis column (numeric)
        title (str): Chart title
        xaxis_title (str): X-axis label
        yaxis_title (str): Y-axis label

    Returns:
        plotly figure
    """
    fig = px.box(
        df,
        x=x,
        y=y,
        title=title
    )

    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        template='plotly_white'
    )

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def create_histogram(df, x, title, xaxis_title, nbins=30):
    """
    Create a histogram

    Args:
        df (pd.DataFrame): Data
        x (str): Column to plot
        title (str): Chart title
        xaxis_title (str): X-axis label
        nbins (int): Number of bins

    Returns:
        plotly figure
    """
    fig = px.histogram(
        df,
        x=x,
        title=title,
        nbins=nbins
    )

    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title="Frekuensi",
        template='plotly_white'
    )

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def create_grouped_bar_chart(df, x, y_columns, title, xaxis_title, yaxis_title):
    """
    Create a grouped bar chart with multiple y columns

    Args:
        df (pd.DataFrame): Data
        x (str): X-axis column
        y_columns (list): List of Y-axis columns
        title (str): Chart title
        xaxis_title (str): X-axis label
        yaxis_title (str): Y-axis label

    Returns:
        plotly figure
    """
    fig = go.Figure()

    for col in y_columns:
        fig.add_trace(go.Bar(
            x=df[x],
            y=df[col],
            name=col
        ))

    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        barmode='group',
        template='plotly_white'
    )

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def create_correlation_heatmap(corr_matrix, title="Matriks Korelasi"):
    """
    Create a correlation heatmap

    Args:
        corr_matrix (pd.DataFrame): Correlation matrix
        title (str): Chart title

    Returns:
        plotly figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        hoverongaps=False
    ))

    fig.update_layout(
        title=title,
        template='plotly_white',
        width=800,
        height=600
    )

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def create_time_series_chart(df, date_col, value_col, title, yaxis_title):
    """
    Create a time series chart

    Args:
        df (pd.DataFrame): Data
        date_col (str): Date column
        value_col (str): Value column
        title (str): Chart title
        yaxis_title (str): Y-axis label

    Returns:
        plotly figure
    """
    fig = px.line(
        df,
        x=date_col,
        y=value_col,
        title=title,
        markers=True
    )

    fig.update_layout(
        xaxis_title="Tanggal",
        yaxis_title=yaxis_title,
        hovermode='x unified',
        template='plotly_white'
    )

    fig.update_xaxes(rangeslider_visible=True)

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def create_multi_line_chart(df, x, y_columns, title, xaxis_title, yaxis_title):
    """
    Create a multi-line chart

    Args:
        df (pd.DataFrame): Data
        x (str): X-axis column
        y_columns (list): List of Y-axis columns
        title (str): Chart title
        xaxis_title (str): X-axis label
        yaxis_title (str): Y-axis label

    Returns:
        plotly figure
    """
    fig = go.Figure()

    for col in y_columns:
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[col],
            mode='lines+markers',
            name=col
        ))

    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        hovermode='x unified',
        template='plotly_white'
    )

    fig = update_plotly_theme(fig)

    # Apply theme
    fig = update_plotly_theme(fig)

    return fig


def format_number(num):
    """
    Format large numbers with K, M suffixes

    Args:
        num (float): Number to format

    Returns:
        str: Formatted number
    """
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:.0f}"
