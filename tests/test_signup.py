"""Tests for signup endpoint."""
import pytest


class TestSignupHappyPath:
    """Test successful signup scenarios."""

    def test_new_student_can_signup(self, client):
        """Arrange-Act-Assert: Verify new student can successfully sign up."""
        # Arrange
        activity = "Art Studio"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        
        # Verify email was added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]

    def test_signup_returns_success_message(self, client):
        """Arrange-Act-Assert: Verify signup returns proper success message."""
        # Arrange
        activity = "Tennis Club"
        email = "alice@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert f"Signed up {email} for {activity}" in data["message"]


class TestSignupValidation:
    """Test signup validation and error cases."""

    def test_duplicate_signup_returns_400(self, client):
        """Arrange-Act-Assert: Verify duplicate signup is rejected."""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_nonexistent_activity_returns_404(self, client):
        """Arrange-Act-Assert: Verify signup to non-existent activity fails."""
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_email_case_sensitive_in_duplicates(self, client):
        """Arrange-Act-Assert: Verify email matching is case-sensitive."""
        # Arrange
        activity = "Gym Class"
        original_email = "john@mergington.edu"  # Already signed up
        different_case_email = "John@mergington.edu"  # Different case
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={different_case_email}",
            params={"email": different_case_email}
        )
        
        # Assert - Should succeed because case is different
        assert response.status_code == 200

    def test_special_characters_in_email_accepted(self, client):
        """Arrange-Act-Assert: Verify special characters in email are accepted."""
        # Arrange
        activity = "Music Band"
        email = "student+test@mergington.edu"  # Email with special char
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200


class TestCapacityOverflowBug:
    """Document capacity overflow bug where students can exceed max_participants."""

    def test_capacity_overflow_allowed_bug(self, client):
        """
        Arrange-Act-Assert: KNOWN ISSUE - Signup allows exceeding max_participants.
        
        This test documents a critical bug: the signup endpoint does NOT validate
        that adding a participant would exceed max_participants. Students can be
        registered beyond capacity limits.
        
        Expected fix: Add check: if len(participants) >= max_participants, 
        raise HTTPException(status_code=400, detail="Activity is full")
        """
        # Arrange
        activity = "Tennis Club"
        max_participants = 10
        
        # Get current participant count
        response = client.get("/activities")
        current_count = len(response.json()[activity]["participants"])
        
        # Add students until we exceed capacity
        for i in range(max_participants):
            email = f"student{i}@mergington.edu"
            
            # Act
            response = client.post(
                f"/activities/{activity}/signup?email={email}",
                params={"email": email}
            )
            
            # Assert - Currently this succeeds even when over capacity (BUG)
            assert response.status_code == 200
        
        # Verify we can add one more, exceeding capacity
        excess_email = "excess_student@mergington.edu"
        response = client.post(
            f"/activities/{activity}/signup?email={excess_email}",
            params={"email": excess_email}
        )
        
        # This should fail but currently succeeds - documenting the bug
        assert response.status_code == 200  # BUG: Should be 400


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_activity_name_with_spaces(self, client):
        """Arrange-Act-Assert: Verify activity names with spaces work correctly."""
        # Arrange
        activity = "Programming Class"  # Has space
        email = "coder@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200

    def test_very_long_email(self, client):
        """Arrange-Act-Assert: Verify very long email addresses are handled."""
        # Arrange
        activity = "Art Studio"
        long_email = "verylongemailaddress" + "x" * 100 + "@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={long_email}",
            params={"email": long_email}
        )
        
        # Assert - Should succeed (no email validation in current app)
        assert response.status_code == 200

    def test_whitespace_in_email(self, client):
        """Arrange-Act-Assert: Verify emails with whitespace are stored as-is."""
        # Arrange
        activity = "Science Olympiad"
        email_with_space = "student with space@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email_with_space}",
            params={"email": email_with_space}
        )
        
        # Assert - No validation, so this succeeds
        assert response.status_code == 200
