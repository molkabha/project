def mock_provenance_check(file_path, file_hash):
    return {
        "score": 82,
        "source": "mock",
        "details": "Provenance data simulated for "
    }

def mock_license_check(file_path):
    return {
        "score": 70,
        "source": "mock",
        "details": "Licence clarity simulated for "
    }

def mock_contamination_check(file_path):
    return {
        "score": 10,
        "source": "mock",
        "details": "Contamination risk simulated for "
    }

def run_mock_api_checks(file_path, file_hash):
    return {
        "provenance": mock_provenance_check(file_path, file_hash),
        "license": mock_license_check(file_path),
        "contamination": mock_contamination_check(file_path)
    }
