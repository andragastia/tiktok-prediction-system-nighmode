"""
Theme Manager - Night Mode Toggle
Handles light/dark theme switching across the application
"""
import streamlit as st

def initialize_theme():
    """Initialize theme in session state if not exists"""
    if 'dark_mode' not in st.session_state:
        st.session_state['dark_mode'] = False

def get_theme():
    """Get current theme setting"""
    initialize_theme()
    return st.session_state.get('dark_mode', False)

def toggle_theme():
    """Toggle between light and dark mode"""
    initialize_theme()
    st.session_state['dark_mode'] = not st.session_state['dark_mode']

def apply_theme():
    """Apply theme CSS based on current mode"""
    is_dark = get_theme()

    if is_dark:
        # Dark mode colors
        bg_color = "#1e1e1e"
        secondary_bg = "#2d2d2d"
        text_color = "#e0e0e0"
        secondary_text = "#a0a0a0"
        border_color = "#404040"
        card_bg = "#2d2d2d"
        card_shadow = "0 2px 4px rgba(0,0,0,0.4)"
        primary_color = "#00f2ea"
        header_color = "#00f2ea"
        metric_bg = "#2d2d2d"
        code_bg = "#1a1a1a"

        theme_css = f"""
        <style>
            /* Main app background */
            .stApp {{
                background-color: {bg_color};
                color: {text_color};
            }}

            /* Sidebar */
            [data-testid="stSidebar"] {{
                background-color: {secondary_bg};
            }}

            /* Headers */
            h1, h2, h3, h4, h5, h6 {{
                color: {text_color} !important;
            }}

            /* Main header styling */
            .main-header {{
                color: {header_color} !important;
            }}

            /* Text elements */
            p, li, label {{
                color: {text_color} !important;
            }}

            /* Metric cards */
            [data-testid="stMetric"] {{
                background-color: {metric_bg};
                padding: 1rem;
                border-radius: 0.5rem;
                border: 1px solid {border_color};
            }}

            [data-testid="stMetricLabel"] {{
                color: {secondary_text} !important;
            }}

            [data-testid="stMetricValue"] {{
                color: {text_color} !important;
            }}

            /* Cards and containers */
            .metric-card {{
                background-color: {card_bg} !important;
                border: 1px solid {border_color};
                box-shadow: {card_shadow};
            }}

            /* Info boxes */
            .stAlert {{
                background-color: {secondary_bg};
                border: 1px solid {border_color};
            }}

            /* Dataframes */
            [data-testid="stDataFrame"] {{
                background-color: {secondary_bg};
                color: {text_color};
            }}

            /* Input fields */
            input, textarea, select {{
                background-color: {secondary_bg} !important;
                color: {text_color} !important;
                border-color: {border_color} !important;
            }}

            /* Buttons */
            .stButton > button {{
                background-color: {secondary_bg};
                color: {text_color};
                border: 1px solid {border_color};
            }}

            .stButton > button:hover {{
                background-color: {border_color};
                border-color: {primary_color};
            }}

            /* Primary buttons */
            .stButton > button[kind="primary"] {{
                background-color: {primary_color};
                color: #000000;
            }}

            /* Expander */
            .streamlit-expanderHeader {{
                background-color: {secondary_bg};
                color: {text_color} !important;
            }}

            /* Code blocks */
            code {{
                background-color: {code_bg} !important;
                color: {primary_color} !important;
            }}

            pre {{
                background-color: {code_bg} !important;
                border: 1px solid {border_color};
            }}

            /* Tables */
            table {{
                background-color: {secondary_bg} !important;
                color: {text_color} !important;
            }}

            th {{
                background-color: {card_bg} !important;
                color: {text_color} !important;
            }}

            /* Plotly charts - dark background */
            .js-plotly-plot {{
                background-color: {bg_color} !important;
            }}

            /* Markdown in dark mode */
            .stMarkdown {{
                color: {text_color};
            }}

            /* Divider */
            hr {{
                border-color: {border_color} !important;
            }}

            /* Success/Warning/Error boxes */
            .stSuccess {{
                background-color: rgba(0, 242, 234, 0.1);
                border-left: 4px solid {primary_color};
            }}

            .stWarning {{
                background-color: rgba(255, 165, 0, 0.1);
                border-left: 4px solid #ffa500;
            }}

            .stError {{
                background-color: rgba(255, 0, 0, 0.1);
                border-left: 4px solid #ff0000;
            }}

            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {{
                background-color: {secondary_bg};
            }}

            .stTabs [data-baseweb="tab"] {{
                color: {text_color} !important;
            }}

            /* File uploader */
            [data-testid="stFileUploader"] {{
                background-color: {secondary_bg};
                border: 1px dashed {border_color};
            }}

            /* Download button */
            .stDownloadButton > button {{
                background-color: {secondary_bg};
                color: {text_color};
                border: 1px solid {border_color};
            }}

            /* Slider */
            .stSlider {{
                color: {text_color};
            }}

            /* Checkbox */
            .stCheckbox {{
                color: {text_color};
            }}

            /* Selectbox */
            [data-baseweb="select"] {{
                background-color: {secondary_bg} !important;
                color: {text_color} !important;
            }}

            /* Number input */
            [data-baseweb="input"] {{
                background-color: {secondary_bg} !important;
                color: {text_color} !important;
            }}
        </style>
        """
    else:
        # Light mode (default)
        bg_color = "#ffffff"
        secondary_bg = "#f0f2f6"
        text_color = "#262730"
        primary_color = "#00f2ea"

        theme_css = f"""
        <style>
            /* Light mode - minimal styling, use defaults */
            .main-header {{
                font-size: 2.5rem;
                font-weight: 700;
                color: {primary_color};
                text-align: center;
                margin-bottom: 1rem;
            }}
            .sub-header {{
                font-size: 1.2rem;
                text-align: center;
                color: #666;
                margin-bottom: 2rem;
            }}
            .metric-card {{
                background-color: {secondary_bg};
                padding: 1.5rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
        </style>
        """

    st.markdown(theme_css, unsafe_allow_html=True)

def show_theme_toggle():
    """Display theme toggle in sidebar"""
    initialize_theme()

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Tema Tampilan")

    is_dark = get_theme()

    # Create toggle button
    col1, col2 = st.sidebar.columns([3, 1])

    with col1:
        if is_dark:
            st.sidebar.write("🌙 Mode Malam Aktif")
        else:
            st.sidebar.write("☀️ Mode Terang Aktif")

    with col2:
        if st.sidebar.button("🔄", key="theme_toggle_btn", help="Ganti tema"):
            toggle_theme()
            st.rerun()

    # Alternative: Use checkbox for toggle
    # new_mode = st.sidebar.checkbox(
    #     "🌙 Mode Malam",
    #     value=is_dark,
    #     key="theme_toggle_checkbox",
    #     help="Aktifkan/nonaktifkan mode malam"
    # )
    # if new_mode != is_dark:
    #     st.session_state['dark_mode'] = new_mode
    #     st.rerun()

def update_plotly_theme(fig):
    """Update Plotly figure to match current theme"""
    is_dark = get_theme()

    if is_dark:
        # Dark mode colors for Plotly
        fig.update_layout(
            paper_bgcolor="#1e1e1e",
            plot_bgcolor="#2d2d2d",
            font=dict(color="#e0e0e0"),
            xaxis=dict(
                gridcolor="#404040",
                zerolinecolor="#404040"
            ),
            yaxis=dict(
                gridcolor="#404040",
                zerolinecolor="#404040"
            ),
            colorway=["#00f2ea", "#ff6b6b", "#ffd93d", "#6bcf7f", "#a78bfa", "#fb923c"]
        )
    else:
        # Light mode (default Plotly theme)
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#262730"),
            colorway=["#00f2ea", "#ff6b6b", "#ffd93d", "#6bcf7f", "#a78bfa", "#fb923c"]
        )

    return fig
