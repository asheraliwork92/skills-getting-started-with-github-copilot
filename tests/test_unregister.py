"""Tests for unregister endpoint."""
import pytest


class TestUnregisterHappyPath:
    """Test successful unregister scenarios."""

    def test_student_can_unregister(self, client):
        """Arrange-Act-Assert: Verify student can successfully unregister."""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify email was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]

    def test_unregister_returns_success_message(self, client):
        """Arrange-Act-Assert: Verify unregister returns proper message."""
        # Arrange
        activity = "Gym Class"
        email = "olivia@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert f"Unregistered {email} from {activity}" in data["message"]


class TestUnregisterValidation:
    """Test unregister validation and error cases."""

    def test_unregister_nonexistent_student_returns_400(self, client):
        """Arrange-Act-Assert: Verify unregistering non-signed-up student fails."""
        # Arrange
        activity = "Art Studio"
        email = "never_signed_up@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Arrange-Act-Assert: Verify unregistering from non-existent activity fails."""
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_case_sensitive(self, client):
        """Arrange-Act-Assert: Verify unregister is case-sensitive."""
        # Arrange
        activity = "Debate Club"
        original_email = "grace@mergington.edu"
        wrong_case_email = "Grace@mergington.edu"
        
        # Act: Try to unregister with wrong case
        response = client.post(
            f"/activities/{activity}/unregister?email={wrong_case_email}",
            params={"email": wrong_case_email}
        )
        
        # Assert: Should fail because case doesn't match
        assert response.status_code == 400
        
        # Verify original email is still there
        activities_response = client.get("/activities")
        assert original_email in activities_response.json()[activity]["participants"]


class TestEdgeCases:
    """Test edge cases for unregister."""

    def test_unregister_then_signup_again(self, client):
        """Arrange-Act-Assert: Verify student can re-signup after unregistering."""
        # Arrange
        activity = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act 1: Unregister
        response1 = client.post(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Act 2: Sign up again
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response2.status_code == 200
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]

    def test_multiple_unregister_attempts_fail_second_time(self, client):
        """Arrange-Act-Assert: Verify second unregister attempt fails."""
        # Arrange
        activity = "Music Band"
        email = "lucas@mergington.edu"
        
        # Act 1: First unregister succeeds
        response1 = client.post(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Act 2: Second unregister should fail
        response2 = client.post(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response2.status_code == 400
