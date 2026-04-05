"""
Test script to verify core functionality without requiring live API.
This simulates parsing a Google Maps API response.
"""
import sys
from route_models import Step, Route
from route_parser import RouteParser
from route_scorer import RouteScorer

# Sample API response structure (simplified)
sample_api_response = [
    {
        "summary": "8th Avenue Express",
        "legs": [
            {
                "duration": {"text": "35 min", "value": 2100},
                "distance": {"text": "8.2 km", "value": 8200},
                "steps": [
                    {
                        "travel_mode": "WALKING",
                        "duration": {"text": "5 min", "value": 300},
                        "distance": {"text": "0.3 km", "value": 300},
                        "html_instructions": "Walk to <b>Times Square</b>"
                    },
                    {
                        "travel_mode": "TRANSIT",
                        "duration": {"text": "25 min", "value": 1500},
                        "distance": {"text": "7.5 km", "value": 7500},
                        "html_instructions": "Take the <b>A</b> train toward <b>Inwood-207 St</b>",
                        "transit_details": {
                            "line": {
                                "name": "A",
                                "vehicle": {"type": "SUBWAY"}
                            },
                            "departure_stop": {"name": "Times Square-42 St"},
                            "arrival_stop": {"name": "59 St-Columbus Circle"}
                        }
                    },
                    {
                        "travel_mode": "WALKING",
                        "duration": {"text": "5 min", "value": 300},
                        "distance": {"text": "0.4 km", "value": 400},
                        "html_instructions": "Walk to <b>Central Park</b>"
                    }
                ]
            }
        ]
    }
]

print("Testing route parsing...")
try:
    routes = RouteParser.parse_routes(sample_api_response)
    print(f"✓ Parsed {len(routes)} route(s)")

    route = routes[0]
    print(f"  Summary: {route.summary}")
    print(f"  Duration: {route.total_duration}")
    print(f"  Transfers: {route.num_transfers}")
    print(f"  Walking: {route.walking_distance}")

    print("\nSteps:")
    for i, step in enumerate(route.steps, 1):
        print(f"  {i}. {step.instruction[:50]}... ({step.transport_mode})")

    print("\nTesting route scoring...")
    scored_routes = RouteScorer.score_routes(routes)
    print(f"✓ Scored routes: {scored_routes[0].score:.2f}")

    print("\n✅ All tests passed!")

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)