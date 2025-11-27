# scoring.py – Blue Tick Data™ 0.1.5 (Insurer Demo Build)

def score_file(metadata, api_checks):
	"""
	Computes a file-level risk score (0–100).
	Phase 1.5 scoring uses simple weighted heuristics
	so the certificate output looks realistic for insurers.
	"""
	score = 100

	# 1. Metadata completeness (0–1)
	meta_comp = api_checks.get("metadata_completeness", 1.0)
	score -= (1 - meta_comp) * 10

	# 2. IP similarity (0–1)
	sim = api_checks.get("similarity_score", 0)
	if sim > 0.7:
		score -= 40
	elif sim > 0.4:
		score -= 25
	elif sim > 0.2:
		score -= 10
	else:
		score -= sim * 5

	# 3. Contamination
	contam = api_checks.get("contamination_risk", "LOW").upper()
	if contam == "MEDIUM":
		score -= 15
	elif contam == "HIGH":
		score -= 35
	elif contam == "CRITICAL":
		score -= 60

	# 4. License mismatch
	if api_checks.get("license_mismatch"):
		score -= 20

	# 5. Safety
	safety = api_checks.get("safety_risk", "LOW").upper()
	if safety == "MEDIUM":
		score -= 15
	elif safety == "HIGH":
		score -= 35

	return max(0, int(score))


def risk_band_from_score(score):
	"""Maps numeric score to qualitative band."""
	if score >= 90:
		return "LOW"
	elif score >= 75:
		return "GUARDED"
	elif score >= 55:
		return "MEDIUM"
	elif score >= 35:
		return "HIGH"
	return "CRITICAL"


def coverage_from_band(band):
	"""Coverage recommendation."""
	table = {
		"LOW": "Full Cover",
		"GUARDED": "75% Cover Recommended",
		"MEDIUM": "Limited Cover",
		"HIGH": "Excluded",
		"CRITICAL": "No Cover"
	}
	return table.get(band, "Limited Cover")


def premium_adjustment_from_band(band):
	"""Premium adjustment guidance."""
	table = {
		"LOW": "+0–5%",
		"GUARDED": "+5–12%",
		"MEDIUM": "+12–20%",
		"HIGH": "+20–30%",
		"CRITICAL": "Decline"
	}
	return table.get(band, "+12–20%")


def aggregate_dataset_score(file_scores):
	"""Weighted mean with penalty for high-risk files."""
	if not file_scores:
		return 0

	base = sum(file_scores) / len(file_scores)
	high_risk = sum(1 for s in file_scores if s < 55)
	penalty = high_risk * 0.4

	return max(0, int(base - penalty))


def score_dataset(files):
	"""Scores all files and dataset-level."""
	scored_files = []
	file_scores = []

	for f in files:
		s = score_file(f.get("metadata", {}), f.get("api_checks", {}))
		band = risk_band_from_score(s)

		scored_files.append({
			**f,
			"score": s,
			"risk_band": band,
			"coverage_level": coverage_from_band(band),
			"premium_adjustment": premium_adjustment_from_band(band)
		})

		file_scores.append(s)

	dataset_score = aggregate_dataset_score(file_scores)
	dataset_band = risk_band_from_score(dataset_score)

	return {
		"dataset_score": dataset_score,
		"dataset_risk_band": dataset_band,
		"dataset_coverage": coverage_from_band(dataset_band),
		"dataset_premium": premium_adjustment_from_band(dataset_band),
		"files": scored_files
	}