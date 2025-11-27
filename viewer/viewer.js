// viewer/viewer.js – Blue Tick Data™ v0.1.5

document.getElementById("loadBtn").addEventListener("click", () => {
	const fileInput = document.getElementById("jsonFileInput").files[0];
	if (!fileInput) {
		alert("Please select a JSON file first.");
		return;
	}

	const reader = new FileReader();

	reader.onload = (e) => {
		try {
			const data = JSON.parse(e.target.result);

			// SHOW PANELS
			document.getElementById("summaryPanel").classList.remove("hidden");
			document.getElementById("jsonViewer").classList.remove("hidden");

			// FILL CERTIFICATE SUMMARY
			const ds = data.dataset;
			const or = data.overall_risk;

			document.getElementById("datasetHash").innerHTML =
				`<b>Dataset Hash:</b> ${ds.dataset_hash}`;

			document.getElementById("manifestHash").innerHTML =
				`<b>Manifest Hash:</b> ${ds.manifest_hash}`;

			document.getElementById("totalFiles").innerHTML =
				`<b>Total Files:</b> ${ds.total_files}`;

			document.getElementById("datasetSize").innerHTML =
				`<b>Dataset Size:</b> ${ds.dataset_size_gb} GB`;

			document.getElementById("mimeBreakdown").innerHTML =
				`<b>MIME Breakdown:</b><br/><pre style="margin-top:5px;">${JSON.stringify(ds.mime_breakdown, null, 2)}</pre>`;

			document.getElementById("overallScore").innerHTML =
				`<b>Overall Score:</b> ${or.score}`;

			document.getElementById("coverageLevel").innerHTML =
				`<b>Coverage:</b> ${or.coverage_level}`;

			document.getElementById("premiumAdjustment").innerHTML =
				`<b>Premium Adjustment:</b> ${or.premium_adjustment}`;

			document.getElementById("claimTriggers").innerHTML =
				`<b>Claim Triggers:</b><br/>${data.claim_triggers.join("<br/>")}`;

			// RISK BAND COLOUR
			const rb = document.getElementById("riskBand");
			rb.innerHTML = or.risk_band;

			const colours = {
				"LOW": "#2ecc71",
				"GUARDED": "#3498db",
				"MEDIUM": "#f1c40f",
				"HIGH": "#e67e22",
				"CRITICAL": "#e74c3c"
			};

			rb.style.background = colours[or.risk_band] || "#ccc";
			rb.style.color = "white";

			// JSON OUTPUT
			document.getElementById("jsonOutput").textContent =
				JSON.stringify(data, null, 4);

			// DOWNLOAD PDF (placeholder for Phase 2)
			document.getElementById("downloadPdfBtn").onclick = () => {
				const pdfPath = data.certificate_id + ".pdf";
				alert(`PDF download would fetch: ${pdfPath}\n\nIn production, this would download the certificate PDF.`);
				// window.location.href = pdfPath;
			};

		} catch (error) {
			alert("Error parsing JSON file: " + error.message);
		}
	};

	reader.readAsText(fileInput);
});