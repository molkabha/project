# main.py – Blue Tick Data™ 0.1.5 (Insurer Demo Build)
# Orchestrates ingestion → hashing → metadata → mock API checks →
# scoring → JSON output → insurer-grade PDF certificate.

import argparse
import json
from pathlib import Path
from datetime import datetime
import uuid

from modules.ingestion import scan_folder
from modules.hashing import compute_dataset_hash
from modules.metadata import extract_metadata
from modules.api_checks import run_api_checks
from modules.scoring import score_dataset
from modules.pdf_generator import generate_pdf


def build_dataset_summary(files):
	"""
	Builds dataset-level summary for JSON & certificate.
	"""
	total_files = len(files)
	total_size_gb = sum(f.get("size_kb", 0) for f in files) / (1024 * 1024)

	# MIME breakdown
	mime_map = {}
	for f in files:
		m = f.get("mime_type", "unknown")
		mime_map[m] = mime_map.get(m, 0) + 1

	return {
		"total_files": total_files,
		"dataset_size_gb": round(total_size_gb, 3),
		"mime_breakdown": mime_map,
		"verification_scope": (
			"Certificate applies ONLY to the dataset hashed at issuance. "
			"Any modification invalidates certification."
		)
	}


def main():
	parser = argparse.ArgumentParser(description="Blue Tick Data™ Verification Tool (v0.1.5)")
	parser.add_argument("-i", "--input", required=True, help="Folder containing dataset files")
	parser.add_argument("-o", "--output", required=True, help="Path for JSON output")
	parser.add_argument("-p", "--pdf", required=True, help="Path for PDF certificate output")
	args = parser.parse_args()

	folder = Path(args.input)

	# ------------------------------------------------------------
	# Load files → metadata + API checks
	# ------------------------------------------------------------
	raw_files = scan_folder(folder)
	processed_files = []

	for f in raw_files:
		metadata = extract_metadata(f["path"])
		f_dict = {
			"filename": f["filename"],
			"sha256": f["sha256"],
			"mime_type": metadata.get("mime_type", "unknown"),
			"size_kb": metadata.get("size_kb", 0),
			"metadata": metadata,
			"api_checks": run_api_checks({
				"mime_type": metadata.get("mime_type", ""),
				"metadata": metadata
			})
		}
		processed_files.append(f_dict)

	# ------------------------------------------------------------
	# Scoring engine
	# ------------------------------------------------------------
	scoring_result = score_dataset(processed_files)

	# ------------------------------------------------------------
	# Dataset-level hashes
	# ------------------------------------------------------------
	dataset_hash = compute_dataset_hash([f["sha256"] for f in processed_files])

	manifest_hash = compute_dataset_hash(
		[f"{f['filename']}:{f['sha256']}" for f in processed_files]
	)

	# ------------------------------------------------------------
	# Dataset Summary
	# ------------------------------------------------------------
	summary = build_dataset_summary(processed_files)

	# ------------------------------------------------------------
	# Build final JSON structure (Phase 1.5 schema)
	# ------------------------------------------------------------
	cert_id = f"BTD-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}"

	output = {
		"certificate_id": cert_id,
		"version": "0.1.5",
		"verified_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),

		"dataset": {
			"dataset_hash": dataset_hash,
			"manifest_hash": manifest_hash,
			**summary
		},

		"overall_risk": {
			"score": scoring_result["dataset_score"],
			"risk_band": scoring_result["dataset_risk_band"],
			"coverage_level": scoring_result["dataset_coverage"],
			"premium_adjustment": scoring_result["dataset_premium"]
		},

		"claim_triggers": [
			"Copyright/IP infringement",
			"Dataset contamination by protected content",
			"Provenance/licensing failure",
			"Regulatory or safety breach",
			"Unauthorized or scraped data sources"
		],

		"commercial": {
			"certificate_fee": None,
			"commission_model": (
				"Blue Tick Data™ operates on a partner commission basis "
				"(details upon request)."
			)
		},

		"files": scoring_result["files"]
	}

	# ------------------------------------------------------------
	# Save JSON
	# ------------------------------------------------------------
	with open(args.output, "w") as f:
		json.dump(output, f, indent=4)

	# ------------------------------------------------------------
	# Generate PDF Certificate
	# ------------------------------------------------------------
	generate_pdf(args.pdf, output)

	print("\n✔ Verification complete.")
	print(f"✔ JSON saved to: {args.output}")
	print(f"✔ Certificate saved to: {args.pdf}")
	print("✔ Blue Tick Data™ v0.1.5")


if __name__ == "__main__":
	main()