from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import sys
import uuid
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from OrchestratorCall import call_orchestrator

app = Flask(__name__, static_folder=".")
CORS(app)

TEMP_DIR = tempfile.mkdtemp(prefix="misfold_pdfs_")


@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory("assets", filename)


@app.route("/api/analyze", methods=["POST"])
def analyze_sequence():
    try:
        data = request.get_json()
        protein_name = data.get("protein_name", "").strip()
        dna_sequence = data.get("dna_sequence", "").strip()

        if not dna_sequence:
            return jsonify({"error": "DNA sequence is required"}), 400

        if not protein_name:
            protein_name = "Unknown_Protein"

        pdf_filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
        pdf_output_path = os.path.join(TEMP_DIR, pdf_filename)

        pdf_path, report_data = call_orchestrator(
            protein_name=protein_name,
            dna_sequence=dna_sequence,
            output_file=pdf_output_path,
        )

        response_data = {
            "status": "success",
            "results": {
                "protein_name": protein_name,
                "anomaly_z_score": report_data.get("anomaly_z_score"),
                "severity_classification": report_data.get("severity_classification"),
                "homolog_information": report_data.get("homolog_information", "N/A"),
                "summary": report_data.get("output", {}).get("raw_text", ""),
                "pdf_url": f"/api/download/{pdf_filename}",
            },
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/download/<filename>", methods=["GET"])
def download_pdf(filename):
    try:
        pdf_path = os.path.join(TEMP_DIR, filename)
        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF file not found"}), 404

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name="protein_analysis_report.pdf",
            mimetype="application/pdf",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
