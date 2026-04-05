"""
Data models for routes and steps using dataclasses.
Clean, type-hinted structures for route information.
"""
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime, time


@dataclass
class Step:
    """Represents a single step in a route"""
    instruction: str
    distance: str
    duration: str
    duration_seconds: int
    transport_mode: str
    line_name: Optional[str] = None
    vehicle_type: Optional[str] = None
    departure_stop: Optional[str] = None
    arrival_stop: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.departure_time:
            data['departure_time'] = self.departure_time.isoformat()
        if self.arrival_time:
            data['arrival_time'] = self.arrival_time.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Step':
        """Create Step from dictionary"""
        # Parse datetime strings if present
        departure_time = None
        arrival_time = None
        if data.get('departure_time'):
            departure_time = datetime.fromisoformat(data['departure_time'])
        if data.get('arrival_time'):
            arrival_time = datetime.fromisoformat(data['arrival_time'])

        return cls(
            instruction=data['instruction'],
            distance=data['distance'],
            duration=data['duration'],
            duration_seconds=data['duration_seconds'],
            transport_mode=data['transport_mode'],
            line_name=data.get('line_name'),
            vehicle_type=data.get('vehicle_type'),
            departure_stop=data.get('departure_stop'),
            arrival_stop=data.get('arrival_stop'),
            departure_time=departure_time,
            arrival_time=arrival_time
        )


@dataclass
class Route:
    """Represents a complete route from origin to destination"""
    summary: str
    total_duration: str
    total_duration_seconds: int
    total_distance: str
    cost: Optional[str] = None
    num_transfers: int = 0
    walking_distance: str = "0 km"
    walking_time: str = "0 min"
    walking_time_seconds: int = 0
    steps: List[Step] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    score: float = 0.0  # Ranking score (higher is better)

    def __post_init__(self):
        """Initialize default empty list if None"""
        if self.steps is None:
            self.steps = []

    def hash(self) -> str:
        """Generate a unique hash for this route (for reviews)"""
        import hashlib
        # Create hash from key route characteristics
        key = f"{self.summary}_{self.total_duration_seconds}_{self.num_transfers}_{self.walking_time_seconds}"
        return hashlib.md5(key.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'summary': self.summary,
            'total_duration': self.total_duration,
            'total_duration_seconds': self.total_duration_seconds,
            'total_distance': self.total_distance,
            'cost': self.cost,
            'num_transfers': self.num_transfers,
            'walking_distance': self.walking_distance,
            'walking_time': self.walking_time,
            'walking_time_seconds': self.walking_time_seconds,
            'steps': [step.to_dict() for step in self.steps],
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'score': self.score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Route':
        """Create Route from dictionary"""
        steps = [Step.from_dict(step_data) for step_data in data.get('steps', [])]

        departure_time = None
        arrival_time = None
        if data.get('departure_time'):
            departure_time = datetime.fromisoformat(data['departure_time'])
        if data.get('arrival_time'):
            arrival_time = datetime.fromisoformat(data['arrival_time'])

        return cls(
            summary=data['summary'],
            total_duration=data['total_duration'],
            total_duration_seconds=data['total_duration_seconds'],
            total_distance=data['total_distance'],
            cost=data.get('cost'),
            num_transfers=data.get('num_transfers', 0),
            walking_distance=data.get('walking_distance', '0 km'),
            walking_time=data.get('walking_time', '0 min'),
            walking_time_seconds=data.get('walking_time_seconds', 0),
            steps=steps,
            departure_time=departure_time,
            arrival_time=arrival_time,
            score=data.get('score', 0.0)
        )


@dataclass
class Review:
    """User review for a route"""
    route_hash: str
    rating: int  # 1-5
    comment: str
    user_id: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'route_hash': self.route_hash,
            'rating': self.rating,
            'comment': self.comment,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Review':
        """Create Review from dictionary"""
        return cls(
            route_hash=data['route_hash'],
            rating=data['rating'],
            comment=data['comment'],
            user_id=data['user_id'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


@dataclass
class RouteRating:
    """Aggregate rating statistics for a route"""
    route_hash: str
    average_rating: float
    review_count: int
    rating_distribution: Dict[int, int]  # {1: count, 2: count, ...}