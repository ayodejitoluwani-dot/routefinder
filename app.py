#!/usr/bin/env python3
"""
Public Transport Route Finder - Main Application

A Streamlit app that finds optimal public transport routes using Google Maps.
"""
import streamlit as st
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from config import Config
from client_factory import ClientFactory
from route_parser import RouteParser
from route_scorer import RouteScorer
from storage import Storage
from ui_components import (
    render_header,
    render_input_form,
    render_route_card,
    render_comparison_table,
    render_sidebar,
    render_error,
    render_success,
    render_loading
)

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Public Transport Route Finder",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main title styling */
    .main .block-container {
        padding-top: 2rem;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ddd;
    }

    /* Better button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        background-color: #ff4b4b;
        color: white;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #ff3333;
        border: none;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-size: 0.9rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'client' not in st.session_state:
        try:
            Config.validate()
            st.session_state.client = ClientFactory.create_client()
            st.session_state.api_ready = True
            st.session_state.provider_name = ClientFactory.get_provider_name()
        except ValueError as e:
            st.session_state.api_ready = False
            st.session_state.api_error = str(e)

    if 'storage' not in st.session_state:
        st.session_state.storage = Storage()

    if 'routes' not in st.session_state:
        st.session_state.routes = []

    if 'last_search' not in st.session_state:
        st.session_state.last_search = None


def main():
    """Main application function."""
    initialize_session_state()

    # Check API configuration
    if not st.session_state.get('api_ready', False):
        st.error(f"⚠️ Configuration Error: {st.session_state.get('api_error', 'Unknown error')}")
        st.markdown("""
        ### Setup Required

        1. Get a Google Maps API key:
           - Go to [Google Cloud Console](https://console.cloud.google.com/)
           - Enable **Directions API**
           - Create an API key

        2. Create a `.env` file in this directory:
        """)
        st.code("""
        GOOGLE_MAPS_API_KEY=your_api_key_here
        """)
        st.markdown("3. Restart the app")
        st.stop()

    # Render header
    render_header()

    # Render sidebar
    render_sidebar(st.session_state.storage, st.session_state.get('provider_name'))

    # Main content area
    main_container = st.container()

    with main_container:
        # Input form
        form_data = render_input_form(
            default_origin=st.session_state.get('last_origin', ''),
            default_destination=st.session_state.get('last_destination', '')
        )

        if form_data:
            origin = form_data['origin']
            destination = form_data['destination']

            # Validate inputs
            if not origin or not destination:
                render_error("Please enter both origin and destination.")
            elif not st.session_state.client.validate_location(origin):
                render_error("Invalid origin. Please enter a valid location.")
            elif not st.session_state.client.validate_location(destination):
                render_error("Invalid destination. Please enter a valid location.")
            else:
                # Save for form persistence
                st.session_state.last_origin = origin
                st.session_state.last_destination = destination

                # Fetch routes
                with render_loading("Fetching routes from Google Maps..."):
                    try:
                        # Determine time parameters
                        departure_time = None
                        if form_data['departure_option'] == "Custom time" and form_data['custom_time']:
                            departure_time = form_data['custom_time']
                        elif form_data['departure_option'] == "Arrival by":
                            # For arrival time, we can't directly specify in API
                            # Google Maps uses departure_time and we'd need to calculate
                            # For now, just use None (we'll show departure time filtering options)
                            st.info("Arrival time filtering requires custom implementation.")
                            departure_time = None

                        # Build request
                        api_response = st.session_state.client.get_routes(
                            origin=origin,
                            destination=destination,
                            departure_time=departure_time,
                            alternatives=True,
                            transit_mode='transit'
                        )

                        # Parse and score routes
                        routes = RouteParser.parse_routes(api_response)
                        routes = RouteScorer.score_routes(routes)
                        routes = routes[:form_data['max_routes']]

                        # Store in session state
                        st.session_state.routes = routes
                        st.session_state.last_search = {
                            'origin': origin,
                            'destination': destination,
                            'timestamp': datetime.now()
                        }

                        if routes:
                            render_success(f"Found {len(routes)} route(s)")
                        else:
                            render_error("No transit routes found. Try different locations or check if public transit is available.")

                    except Exception as e:
                        render_error(f"Error: {str(e)}")
                        st.exception(e) if st.checkbox("Show detailed error", key="show_error") else None

        # Display results if available
        if st.session_state.routes:
            st.markdown("---")
            st.markdown(f"## Routes from {st.session_state.last_search['origin']} to {st.session_state.last_search['destination']}")

            # Create tabs for different views
            tab_details, tab_compare = st.tabs(["📋 Route Details", "📊 Comparison Table"])

            with tab_details:
                for i, route in enumerate(st.session_state.routes):
                    render_route_card(
                        route=route,
                        index=i,
                        storage=st.session_state.storage,
                        show_steps=True,
                        expanded=(i == 0)  # Expand first route by default
                    )

            with tab_compare:
                render_comparison_table(st.session_state.routes)

        # Show search history in sidebar or expander
        if st.session_state.get('last_search'):
            with st.expander("🕐 Last Search", expanded=False):
                last = st.session_state.last_search
                st.write(f"**From:** {last['origin']}")
                st.write(f"**To:** {last['destination']}")
                st.write(f"**Time:** {last['timestamp'].strftime('%I:%M %p')}")


if __name__ == "__main__":
    # This allows running with: streamlit run app.py
    # This is the brain of the web app that controls the flow
    main()
