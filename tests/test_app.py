from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_read_root():
    """Test that the root endpoint redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307
    if response.status_code == 307:
        assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Test structure of an activity
    activity = list(activities.values())[0]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get first activity name
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    # Test successful signup
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert email in client.get("/activities").json()[activity_name]["participants"]
    
    # Test duplicate signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First, sign up a student
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    email = "tempstudent@mergington.edu"
    
    # Sign up the student first
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Test successful unregistration
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert email not in client.get("/activities").json()[activity_name]["participants"]
    
    # Test unregistering a student who isn't registered
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()


def test_activity_not_found():
    """Test error handling for non-existent activities"""
    fake_activity = "NonExistentActivity"
    email = "student@mergington.edu"
    
    # Test signup for non-existent activity
    response = client.post(f"/activities/{fake_activity}/signup?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    # Test unregister from non-existent activity
    response = client.delete(f"/activities/{fake_activity}/unregister?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()