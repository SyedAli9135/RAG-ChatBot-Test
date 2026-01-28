import pytest_check as check


def test_root_endpoint(client):
    """Root endpoint responds, verify we must.

    Alive the API is, confirm it should.
    """
    response = client.get("/")

    check.equal(response.status_code, 200, "Status code wrong, it is!")
    data = response.json()
    check.is_in("message", data, "Message missing, it is!")
    check.is_in("version", data, "Version missing, it is!")


def test_health_endpoint(client):
    """Health check working, ensure we must.

    Status healthy, report it should.
    """
    response = client.get("/health")

    check.equal(response.status_code, 200, "Status code wrong, it is!")
    data = response.json()
    check.equal(data["status"], "healthy", "Health status wrong, it is!")
    check.is_in("llm_model", data, "LLM model missing, it is!")
