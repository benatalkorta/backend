"""API for health and version information."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_dp_health_endpoint():
    """Get DataPlatform health endpoint."""
    return config.get_dp_api_endpoint() + "/actuator/health"


def get_dp_info_endpoint():
    """Get DataPlatform version endpoint."""
    return config.get_dp_api_endpoint() + "/actuator/info"


def get_di_health_endpoint():
    """Get DataPlatform health endpoint."""
    return config.get_di_api_endpoint() + "/health"


def get_di_version_endpoint():
    """Get DataPlatform version endpoint."""
    return config.get_di_api_endpoint() + "/version"


def get_dp_version():
    """GET version of DataPlatform."""
    response = None
    url = get_dp_info_endpoint()
    try:
        response = send_request(url)
    except Exception:  # pylint: disable=broad-except
        response = None
        # TODO: checking health status needs to be improved
    if response is None:
        url = url.replace("/actuator", "")
        response = send_request(url)
    result = json.loads(response)
    return result["version"]


def dp_is_healthy():
    """Check status of DataIntegration."""
    url = get_dp_health_endpoint()
    try:
        response = send_request(url)
    except Exception:  # pylint: disable=broad-except
        response = None
        # TODO: checking health status needs to be improved
    if response is None:
        url = url.replace("/actuator", "")
        response = send_request(url)
    result = json.loads(response)
    if result['status'] == "UP":
        return True
    return False


def get_di_version():
    """GET version of DataIntegration."""
    response = send_request(get_di_version_endpoint())
    return response.decode("utf-8")


def di_is_healthy():
    """Check status of DataIntegration."""
    try:
        result = json.loads(send_request(get_di_health_endpoint()))
    except ValueError:
        return False
    if result['status'] == "UP":
        return True
    return False
