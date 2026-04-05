"""
Parse Google Maps API responses into Route objects.
Converts raw API data into structured, typed data models.
"""
from typing import Dict, List, Any
from datetime import datetime
from route_models import Route, Step


class RouteParser:
    """
    Parser for Google Maps Directions API responses.
    Transforms raw JSON into clean Python data structures.
    """

    @staticmethod
    def parse_routes(api_response: List[Dict]) -> List[Route]:
        """
        Parse the complete API response into Route objects.

        Args:
            api_response: List of route dictionaries from Google Maps API

        Returns:
            List of parsed Route objects
        """
        routes = []
        for route_data in api_response:
            try:
                route = RouteParser._parse_route(route_data)
                routes.append(route)
            except Exception as e:
                # Skip malformed routes but continue parsing others
                print(f"Warning: Failed to parse route: {e}")
                continue

        return routes

    @staticmethod
    def _parse_route(route_data: Dict) -> Route:
        """
        Parse a single route from API response.

        Args:
            route_data: Single route dictionary from API

        Returns:
            Parsed Route object
        """
        legs = route_data.get('legs', [])
        if not legs:
            raise ValueError("Route has no legs")

        leg = legs[0]  # Single origin-destination pair

        # Parse steps - returns (steps list, walking_distance_meters, walking_seconds)
        steps, walking_distance_meters, walking_seconds = RouteParser._parse_steps(leg.get('steps', []))

        # Calculate transfers
        num_transfers = RouteParser._count_transfers(steps)

        # Get departure/arrival times
        departure_time = None
        if leg.get('departure_time'):
            dep_ts = leg['departure_time'].get('value')
            if dep_ts:
                departure_time = datetime.fromtimestamp(dep_ts)

        arrival_time = None
        if leg.get('arrival_time'):
            arr_ts = leg['arrival_time'].get('value')
            if arr_ts:
                arrival_time = datetime.fromtimestamp(arr_ts)

        # Parse cost if available (fare information)
        cost = None
        if 'fare' in route_data:
            fare = route_data['fare']
            if 'text' in fare:
                cost = fare['text']

        # Format walking distance as km
        walking_distance_km = walking_distance_meters / 1000
        walking_distance_str = f"{walking_distance_km:.1f} km"

        # Format walking time
        walking_minutes = walking_seconds // 60
        walking_time_str = f"{walking_minutes} min"

        # Format total duration
        total_duration_seconds = leg['duration']['value']
        total_duration_str = leg['duration']['text']

        # Format total distance
        total_distance_meters = leg['distance']['value']
        total_distance_km = total_distance_meters / 1000
        total_distance_str = f"{total_distance_km:.1f} km"

        return Route(
            summary=route_data.get('summary', 'No summary'),
            total_duration=total_duration_str,
            total_duration_seconds=total_duration_seconds,
            total_distance=total_distance_str,
            cost=cost,
            num_transfers=num_transfers,
            walking_distance=walking_distance_str,
            walking_time=walking_time_str,
            walking_time_seconds=walking_seconds,
            steps=steps,
            departure_time=departure_time,
            arrival_time=arrival_time,
            score=0.0
        )

    @staticmethod
    def _parse_steps(steps_data: List[Dict]) -> tuple[List[Step], int, int]:
        """
        Parse steps and calculate walking totals.

        Returns:
            Tuple of (steps list, walking_distance_meters, walking_seconds)
        """
        steps = []
        walking_distance_meters = 0
        walking_seconds = 0

        for step in steps_data:
            # Get distance and duration in meters/seconds
            distance_value = step['distance']['value']
            duration_value = step['duration']['value']
            transport_mode = step['travel_mode'].lower()

            step_obj = Step(
                instruction=step.get('html_instructions', ''),
                distance=step['distance']['text'],
                duration=step['duration']['text'],
                duration_seconds=duration_value,
                transport_mode=transport_mode
            )

            # Add transit-specific details
            if transport_mode == 'transit':
                transit_details = step.get('transit_details', {})
                step_obj.line_name = transit_details.get('line', {}).get('name')
                step_obj.vehicle_type = transit_details.get('line', {}).get('vehicle', {}).get('type')
                step_obj.departure_stop = transit_details.get('departure_stop', {}).get('name')
                step_obj.arrival_stop = transit_details.get('arrival_stop', {}).get('name')

                # Parse departure/arrival times for transit steps
                if 'departure_time' in transit_details:
                    dep_ts = transit_details['departure_time'].get('value')
                    if dep_ts:
                        step_obj.departure_time = datetime.fromtimestamp(dep_ts)
                if 'arrival_time' in transit_details:
                    arr_ts = transit_details['arrival_time'].get('value')
                    if arr_ts:
                        step_obj.arrival_time = datetime.fromtimestamp(arr_ts)

            # Track walking
            if transport_mode == 'walking':
                walking_distance_meters += distance_value
                walking_seconds += duration_value

            steps.append(step_obj)

        return steps, walking_distance_meters, walking_seconds

    @staticmethod
    def _count_transfers(steps: List[Step]) -> int:
        """
        Count number of transfers (transit line changes) in a route.

        Args:
            steps: List of steps in the route

        Returns:
            Number of transfers (0 means direct route)
        """
        transit_lines = []
        for step in steps:
            if step.transport_mode == 'transit' and step.line_name:
                transit_lines.append(step.line_name)

        # A transfer occurs when the line changes
        if len(transit_lines) <= 1:
            return 0

        transfers = 0
        current_line = transit_lines[0]
        for line in transit_lines[1:]:
            if line != current_line:
                transfers += 1
                current_line = line

        return transfers