"""
Reusable Streamlit UI components for the route finder app.
Provides consistent styling and functionality across views.
"""
import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
from typing import List, Optional, Callable
from route_models import Route
from storage import Storage
from config import Config


def render_header():
    """Render the app header."""
    st.title("🚇 Public Transport Route Finder")
    st.markdown("Find the best public transit routes between two locations")


def render_input_form(
    default_origin: str = "",
    default_destination: str = ""
) -> dict:
    """
    Render the main input form.

    Returns:
        Dictionary with form values if submitted, None otherwise
    """
    with st.form("route_form"):
        col1, col2 = st.columns(2)
        with col1:
            origin = st.text_input(
                "Origin",
                value=default_origin,
                placeholder="e.g., Times Square, New York",
                key="origin_input"
            )
        with col2:
            destination = st.text_input(
                "Destination",
                value=default_destination,
                placeholder="e.g., Central Park, New York",
                key="destination_input"
            )

        col3, col4, col5 = st.columns(3)
        with col3:
            departure_option = st.selectbox(
                "Time",
                ["Now", "Arrival by", "Custom time"],
                index=0,
                key="departure_option"
            )
        with col4:
            include_traffic = st.checkbox(
                "Real-time traffic",
                value=False,
                key="traffic_checkbox",
                help="Include current traffic conditions in duration estimates"
            )
        with col5:
            max_routes = st.slider(
                "Max routes",
                min_value=1,
                max_value=5,
                value=3,
                key="max_routes_slider"
            )

        # Custom time input if selected
        custom_time = None
        if departure_option == "Custom time":
            date_col, time_col = st.columns(2)
            with date_col:
                custom_date = st.date_input("Date", key="custom_date")
            with time_col:
                custom_time_val = st.time_input("Time", key="custom_time_val")
            if custom_date and custom_time_val:
                from datetime import datetime
                custom_time = datetime.combine(custom_date, custom_time_val)

        submit = st.form_submit_button(
            "🔍 Find Routes",
            use_container_width=True,
            type="primary"
        )

    if submit:
        return {
            'origin': origin.strip(),
            'destination': destination.strip(),
            'departure_option': departure_option,
            'custom_time': custom_time,
            'include_traffic': include_traffic,
            'max_routes': max_routes
        }
    return None


def render_route_card(
    route: Route,
    index: int,
    storage: Storage,
    show_steps: bool = True,
    expanded: bool = False
):
    """
    Display a single route as a styled card.

    Args:
        route: The Route object to display
        index: Index in the route list (for unique keys)
        storage: Storage instance for fetching ratings
        show_steps: Whether to show step-by-step directions
        expanded: Whether the steps expander should be open by default
    """
    with st.container():
        # Route header with summary and rank badge
        col_header, col_score = st.columns([4, 1])
        with col_header:
            st.markdown(f"### Option {index + 1}: {route.summary}")
        with col_score:
            if route.score > 0.7:
                st.success("⭐ Best")
            elif route.score > 0.5:
                st.info("👍 Good")
            else:
                st.warning("⚠️ Slower")

        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Duration", route.total_duration)
        with col2:
            st.metric("Distance", route.total_distance)
        with col3:
            st.metric("Walking", route.walking_distance)
        with col4:
            st.metric("Transfers", str(route.num_transfers))

        # Display cost if available
        if route.cost:
            st.write(f"**Fare:** {route.cost}")

        # Rating display if available
        avg_rating = storage.get_average_rating(route.hash())
        review_count = storage.get_review_count(route.hash())
        if avg_rating:
            stars = "⭐" * int(round(avg_rating))
            st.write(f"{stars} **{avg_rating:.1f}/5** ({review_count} review{'s' if review_count != 1 else ''})")

        # Departure/arrival times
        if route.departure_time or route.arrival_time:
            time_info = []
            if route.departure_time:
                time_info.append(f"Depart: {route.departure_time.strftime('%I:%M %p')}")
            if route.arrival_time:
                time_info.append(f"Arrive: {route.arrival_time.strftime('%I:%M %p')}")
            st.caption(" | ".join(time_info))

        st.divider()

        # Expandable step-by-step directions
        if show_steps and route.steps:
            with st.expander(f"📋 View Step-by-Step Directions ({len(route.steps)} steps)", expanded=expanded):
                RouteCardStepsDisplay(route).render()

        # Review section (as a separate expander)
        with st.expander("📝 Rate this route"):
            render_review_form(route, storage, index)

        st.markdown("<br>", unsafe_allow_html=True)


class RouteCardStepsDisplay:
    """Helper class for rendering route steps in a nice format."""

    def __init__(self, route: Route):
        self.route = route

    def render(self):
        """Render all steps with icons and styling."""
        for i, step in enumerate(self.route.steps, 1):
            self._render_step(step, i)
            st.write("")  # Spacing

    def _render_step(self, step, step_num: int):
        """Render a single step with appropriate icon."""
        transport_icons = {
            'walking': '🚶',
            'transit': '🚌',
            'subway': '🚇',
            'train': '🚆',
            'bus': '🚌',
            'tram': '🚊'
        }

        vehicle_type = step.vehicle_type or step.transport_mode
        icon = transport_icons.get(vehicle_type.lower(), '📍')

        st.markdown(f"**{step_num}. {icon} {self._clean_html_instructions(step.instruction)}**")

        # Show transit details
        if step.transport_mode == 'transit':
            details = []
            if step.line_name:
                details.append(f"Line: {step.line_name}")
            if step.vehicle_type:
                details.append(f"Vehicle: {step.vehicle_type}")
            if step.departure_stop:
                details.append(f"From: {step.departure_stop}")
            if step.arrival_stop:
                details.append(f"To: {step.arrival_stop}")
            if details:
                st.caption(" • ".join(details))

        # Show duration and distance
        col1, col2 = st.columns([1, 1])
        with col1:
            st.caption(f"⏱️ {step.duration}")
        with col2:
            st.caption(f"📏 {step.distance}")

    @staticmethod
    def _clean_html_instructions(html_text: str) -> str:
        """Remove HTML tags from instructions."""
        import re
        # Remove common HTML tags
        clean = re.sub(r'<[^>]+>', '', html_text)
        # Replace HTML entities
        clean = clean.replace('&nbsp;', ' ')
        clean = clean.replace('&amp;', '&')
        return clean.strip()


def render_review_form(route: Route, storage: Storage, index: int):
    """
    Render a form for submitting route reviews.

    Args:
        route: Route being reviewed
        storage: Storage instance
        index: Unique identifier for the form
    """
    user_id = st.text_input(
        "Your name (optional)",
        value="",
        key=f"review_user_{index}",
        placeholder="Anonymous"
    )
    if not user_id:
        user_id = "anon"

    rating = st.slider(
        "Your rating",
        min_value=1,
        max_value=5,
        value=5,
        key=f"rating_{index}",
        help="1 = terrible, 5 = excellent"
    )

    comment = st.text_area(
        "Comments (optional)",
        value="",
        key=f"comment_{index}",
        placeholder="Share your experience with this route..."
    )

    if st.button("Submit Review", key=f"submit_review_{index}", type="primary"):
        try:
            storage.add_review(
                route_hash=route.hash(),
                rating=rating,
                comment=comment,
                user_id=user_id
            )
            st.success("✅ Thank you for your review!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save review: {e}")


def render_comparison_table(routes: List[Route]):
    """
    Render a side-by-side comparison table of all routes.

    Args:
        routes: List of Route objects to compare
    """
    st.markdown("### 📊 Route Comparison")

    data = []
    for i, route in enumerate(routes):
        walking_minutes = route.walking_time_seconds // 60 if hasattr(route, 'walking_time_seconds') else 0
        data.append({
            "Route": f"Option {i+1}",
            "Summary": route.summary,
            "Duration": route.total_duration,
            "Distance": route.total_distance,
            "Walking": f"{route.walking_distance} ({walking_minutes} min)",
            "Transfers": route.num_transfers,
            "Fare": route.cost or "N/A",
            "Score": f"{route.score:.1%}" if route.score > 0 else "N/A"
        })

    if not data:
        st.info("No routes to compare.")
        return

    df = pd.DataFrame(data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                help="Overall route quality score",
                format="%.0f%%",
                min_value=0,
                max_value=100
            )
        }
    )


def render_sidebar(storage: Storage, provider_name: str = None) -> dict:
    """
    Render the sidebar with about info and stats.

    Args:
        storage: Storage instance
        provider_name: Name of the map provider (e.g., "Google Maps", "HERE Maps")

    Returns:
        Dictionary with sidebar info
    """
    if provider_name is None:
        provider_name = Config.MAPS_PROVIDER.title() if Config.MAPS_PROVIDER else "Google Maps"

    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown(f"""
        This app finds the best public transport routes using **{provider_name}**.

        **Features:**
        - 📍 Multiple route options
        - ⏱️ Duration, walking, transfers
        - 📋 Step-by-step directions
        - ⭐ User reviews & ratings
        - 🗺️ Transit line details
        """)

        st.divider()

        st.subheader("📈 Stats")
        total_reviews = len(storage._read_data().get("reviews", []))
        total_favorites = len(storage._read_data().get("favorites", []))
        st.metric("Total Reviews", total_reviews)
        st.metric("Saved Routes", total_favorites)

        st.divider()

        st.subheader("⚙️ Settings")
        st.write(f"Max routes shown: {Config.MAX_ROUTES}")
        st.write("Storage: JSON file")
        st.caption("v1.0.0")

        st.divider()

        st.markdown("""
        **Made with:**
        - Python 🐍
        - Streamlit ⚡
        - Google Maps API 🗺️
        """)


def render_error(message: str):
    """Render an error message."""
    st.error(f"❌ {message}")


def render_success(message: str):
    """Render a success message."""
    st.success(f"✅ {message}")


def render_loading(message: str = "Loading..."):
    """Render a loading spinner with custom message."""
    return st.spinner(message)