# api_checks.py – Blue Tick Data™ 0.1.5
import random

def mock_similarity_score(file):
	mime = file.get("mime_type", "").lower()
	if "image" in mime:
		return round(random.uniform(0.05, 0.35), 2)
	if "audio" in mime or "video" in mime:
		return round(random.uniform(0.10, 0.45), 2)
	if "pdf" in mime:
		return round(random.uniform(0.02, 0.20), 2)
	if "text" in mime or mime.endswith("json"):
		return round(random.uniform(0.00, 0.10), 2)
	return round(random.uniform(0.05, 0.25), 2)


def mock_contamination_risk(similarity):
	if similarity > 0.7:
		return "CRITICAL"
	elif similarity > 0.4:
		return "HIGH"
	elif similarity > 0.2:
		return "MEDIUM"
	return "LOW"


def mock_license_mismatch(file):
	meta = file.get("metadata", {})
	similarity = file.get("similarity_score", 0)

	if not meta:
		return True

	mime = file.get("mime_type", "").lower()
	if similarity > 0.35 and ("image" in mime or "audio" in mime or "pdf" in mime):
		return True

	return False


def mock_safety_risk(file):
	mime = file.get("mime_type", "").lower()

	if "audio" in mime or "video" in mime:
		r = random.random()
		if r < 0.8:
			return "LOW"
		elif r < 0.95:
			return "MEDIUM"
		return "HIGH"

	if "text" in mime or "pdf" in mime:
		return "LOW"

	return "LOW"


def mock_metadata_completeness(file):
	return round(random.uniform(0.75, 1.00), 2)


def run_api_checks(file):
	similarity = mock_similarity_score(file)
	contamination = mock_contamination_risk(similarity)

	return {
		"similarity_score": similarity,
		"contamination_risk": contamination,
		"license_mismatch": mock_license_mismatch({**file, "similarity_score": similarity}),
		"safety_risk": mock_safety_risk(file),
		"metadata_completeness": mock_metadata_completeness(file)
	}