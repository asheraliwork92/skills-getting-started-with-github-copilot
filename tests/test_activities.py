"""Tests for activity listing endpoints."""
import pytest


class TestGetActivities:
    """Test GET /activities endpoint."""

    def test_get_all_activities(self, client):
        """Arrange-Act-Assert: Verify all activities are returned with correct structure."""
        # Arrange: No setup needed, activities fixture provides data
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_has_required_fields(self, client):
        """Arrange-Act-Assert: Verify each activity has all required fields."""
        # Arrange: Expected fields
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, details in activities.items():
            assert all(field in details for field in required_fields), \
                f"Activity '{activity_name}' missing required fields"

    def test_participants_is_list(self, client):
        """Arrange-Act-Assert: Verify participants field is always a list."""
        # Arrange: None
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, details in activities.items():
            assert isinstance(details["participants"], list), \
                f"Participants for '{activity_name}' is not a list"

    def test_max_participants_is_integer(self, client):
        """Arrange-Act-Assert: Verify max_participants is an integer."""
        # Arrange: None
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, details in activities.items():
            assert isinstance(details["max_participants"], int), \
                f"max_participants for '{activity_name}' is not an integer"

    def test_chess_club_initial_state(self, client):
        """Arrange-Act-Assert: Verify Chess Club has expected initial state."""
        # Arrange: Expected initial participants
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        
        # Assert
        assert chess_club["participants"] == expected_participants
        assert chess_club["max_participants"] == 12


class TestRootRedirect:
    """Test GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """Arrange-Act-Assert: Verify root redirects to static index.html."""
        # Arrange: None
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code in [307, 308, 302, 301]
        assert "location" in response.headers or "Location" in response.headers
        assert "/static/index.html" in response.headers.get("location", "").lower() or \
               "/static/index.html" in response.headers.get("Location", "").lower()
