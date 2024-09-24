import pytest
from fastapi.testclient import TestClient

from dsc_hackai.main import app

client = TestClient(app)

video_file = {
    "video_file": ("test_video.webm", open("dsc_hackai/test_video.webm", "rb"))
}


@pytest.fixture(scope="class")
def process_id_fixture(request):
    request.cls.process_id = None
    yield


@pytest.mark.usefixtures("process_id_fixture")
class TestAnalysis:
    def test_upload_video(self):
        response = client.post("/api/v1/analysis", files=video_file)
        assert response.status_code == 200
        response_data = response.json()
        # Set process_id as a class attribute
        TestAnalysis.process_id = response_data["process_id"]

    def test_get_processing_status(self):
        # Ensure that the process_id exists
        assert (
            TestAnalysis.process_id is not None
        ), "Upload a video first to get a process ID"
        response = client.get(f"/api/v1/analysis/stage/{TestAnalysis.process_id}")
        response_data = response.json()
        assert response.status_code == 200
