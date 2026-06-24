"""
App web para generar videos verticales (Reels/Shorts) automáticamente
a partir de un guion (texto + palabra clave por escena).
"""
import os
import uuid
import threading
import traceback
from flask import Flask, request, render_template, send_from_directory, jsonify

from pipeline import generate_video
from tts_client import VOICE_ES_MEXICO, VOICE_ES_ESPANA_MUJER, VOICE_ES_ESPANA_HOMBRE

app = Flask(__name__)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("temp", exist_ok=True)

VOICES = {
    "mexico_hombre": VOICE_ES_MEXICO,
    "espana_mujer": VOICE_ES_ESPANA_MUJER,
    "espana_hombre": VOICE_ES_ESPANA_HOMBRE,
}

# Estado de los jobs en memoria: {job_id: {"status": "...", "download_url": "...", "error": "..."}}
JOBS = {}


def _run_job(job_id, scenes, voice, music_key):
    try:
        JOBS[job_id] = {"status": "processing", "progress_text": "Iniciando...", "progress_pct": 0}

        def on_progress(text, percent):
            JOBS[job_id] = {"status": "processing", "progress_text": text, "progress_pct": percent}

        final_path = generate_video(scenes, music_key=music_key, voice=voice, job_id=job_id, on_progress=on_progress)
        filename = os.path.basename(final_path)
        JOBS[job_id] = {"status": "done", "download_url": f"/download/{filename}"}
    except Exception as e:
        traceback.print_exc()
        JOBS[job_id] = {"status": "error", "error": str(e)}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    Espera JSON:
    {
        "scenes": [{"text": "...", "keyword": "..."}, ...],
        "voice": "mexico_hombre" | "espana_mujer" | "espana_hombre"
    }
    Devuelve inmediatamente un job_id; el video se genera en background.
    """
    data = request.get_json(force=True)
    scenes = data.get("scenes", [])
    voice_key = data.get("voice", "mexico_hombre")
    music_key = data.get("music", "mystery")

    if not scenes or len(scenes) == 0:
        return jsonify({"error": "Debes agregar al menos una escena (texto + palabra clave)."}), 400

    for s in scenes:
        if not s.get("text") or not s.get("keyword"):
            return jsonify({"error": "Cada escena necesita texto y palabra clave."}), 400

    voice = VOICES.get(voice_key, VOICE_ES_MEXICO)

    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {"status": "processing"}

    thread = threading.Thread(target=_run_job, args=(job_id, scenes, voice, music_key), daemon=True)
    thread.start()

    return jsonify({"ok": True, "job_id": job_id})


@app.route("/api/status/<job_id>")
def api_status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job no encontrado."}), 404
    return jsonify(job)


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
