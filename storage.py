"""
Data persistence layer for user reviews and favorites.
Uses JSON file storage for simplicity (can be upgraded to SQLite later).
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from route_models import Review, RouteRating
from config import Config


class Storage:
    """
    JSON-based storage for route reviews and user favorites.
    Thread-safe for Streamlit's single-threaded execution.
    """

    def __init__(self, filepath: str = None):
        """
        Initialize storage with a JSON file.

        Args:
            filepath: Path to JSON file. If None, uses Config.STORAGE_PATH
        """
        self.filepath = filepath or Config.STORAGE_PATH
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create storage file with initial structure if it doesn't exist."""
        if not os.path.exists(self.filepath):
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            self._initialize_file()

    def _initialize_file(self):
        """Create empty storage structure."""
        initial_data = {
            "reviews": [],
            "favorites": []
        }
        with open(self.filepath, 'w') as f:
            json.dump(initial_data, f, indent=2)

    def _read_data(self) -> Dict:
        """Read all data from storage file."""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Corruption or missing file, reinitialize
            self._initialize_file()
            return {"reviews": [], "favorites": []}

    def _write_data(self, data: Dict):
        """Write all data to storage file."""
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def add_review(
        self,
        route_hash: str,
        rating: int,
        comment: str = "",
        user_id: str = "anon"
    ) -> bool:
        """
        Add a user review for a route.

        Args:
            route_hash: Unique hash of the route
            rating: Rating from 1 to 5
            comment: Optional comment
            user_id: User identifier (defaults to "anon")

        Returns:
            True if successful
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        review = Review(
            route_hash=route_hash,
            rating=rating,
            comment=comment,
            user_id=user_id,
            timestamp=datetime.now()
        )

        data = self._read_data()
        data["reviews"].append(review.to_dict())
        self._write_data(data)

        return True

    def get_reviews(self, route_hash: str) -> List[Review]:
        """
        Get all reviews for a specific route.

        Args:
            route_hash: Unique hash of the route

        Returns:
            List of Review objects
        """
        data = self._read_data()
        reviews = []
        for review_data in data.get("reviews", []):
            if review_data.get("route_hash") == route_hash:
                reviews.append(Review.from_dict(review_data))
        return reviews

    def get_average_rating(self, route_hash: str) -> Optional[float]:
        """
        Calculate average rating for a route.

        Args:
            route_hash: Unique hash of the route

        Returns:
            Average rating (1-5) or None if no reviews
        """
        reviews = self.get_reviews(route_hash)
        if not reviews:
            return None
        return sum(r.rating for r in reviews) / len(reviews)

    def get_review_count(self, route_hash: str) -> int:
        """Get number of reviews for a route."""
        return len(self.get_reviews(route_hash))

    def get_rating_stats(self, route_hash: str) -> Optional[RouteRating]:
        """
        Get comprehensive rating statistics for a route.

        Args:
            route_hash: Unique hash of the route

        Returns:
            RouteRating object with statistics or None if no reviews
        """
        reviews = self.get_reviews(route_hash)
        if not reviews:
            return None

        # Calculate distribution
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            distribution[review.rating] += 1

        return RouteRating(
            route_hash=route_hash,
            average_rating=sum(r.rating for r in reviews) / len(reviews),
            review_count=len(reviews),
            rating_distribution=distribution
        )

    def add_favorite(self, route_hash: str, user_id: str = "anon", notes: str = "") -> bool:
        """
        Save a route as favorite.

        Args:
            route_hash: Unique hash of the route
            user_id: User identifier
            notes: Optional notes about why it's a favorite

        Returns:
            True if successful
        """
        data = self._read_data()

        # Check if already favorited
        for fav in data.get("favorites", []):
            if fav.get("route_hash") == route_hash and fav.get("user_id") == user_id:
                # Update notes if provided
                if notes:
                    fav["notes"] = notes
                    self._write_data(data)
                return True

        # Add new favorite
        favorite = {
            "route_hash": route_hash,
            "user_id": user_id,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        data.setdefault("favorites", []).append(favorite)
        self._write_data(data)

        return True

    def get_favorites(self, user_id: Optional[str] = None) -> List[Dict]:
        """
        Get saved favorite routes.

        Args:
            user_id: If provided, filter by user. If None, returns all favorites.

        Returns:
            List of favorite dictionaries
        """
        data = self._read_data()
        favorites = data.get("favorites", [])

        if user_id:
            favorites = [f for f in favorites if f.get("user_id") == user_id]

        return favorites

    def remove_favorite(self, route_hash: str, user_id: str = "anon") -> bool:
        """
        Remove a route from favorites.

        Args:
            route_hash: Hash of the route to remove
            user_id: User who saved the favorite

        Returns:
            True if removed, False if not found
        """
        data = self._read_data()
        initial_count = len(data.get("favorites", []))

        data["favorites"] = [
            f for f in data.get("favorites", [])
            if not (f.get("route_hash") == route_hash and f.get("user_id") == user_id)
        ]

        if len(data["favorites"]) < initial_count:
            self._write_data(data)
            return True
        return False

    def clear_all_data(self):
        """Delete all reviews and favorites (use with caution)."""
        self._initialize_file()