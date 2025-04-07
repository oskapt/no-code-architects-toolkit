from flask import Blueprint, request, jsonify, current_app
import os
import json

plugin_bp = Blueprint("text_extraction", __name__)


@plugin_bp.route("/", methods=["GET"])
def index():
    """Plugin info endpoint"""
    # Read plugin settings from config
    plugins_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "enabled_plugins.json"
    )
    settings = {}

    if os.path.exists(plugins_dir):
        with open(plugins_dir, "r") as f:
            config = json.load(f)
            settings = config.get("plugin_settings", {}).get("text_extraction", {})

    return jsonify(
        {
            "name": "Text Extraction Plugin",
            "description": "A plugin for extracting text from images and PDFs using OCR",
            "version": "1.0.0",
            "settings": settings,
        }
    )


@plugin_bp.route("/ocr", methods=["POST"])
def extract_text():
    """
    Extract text from an image or PDF using OCR
    Expected JSON payload:
    {
        "media_url": "https://example.com/document.pdf",
        "language": "eng",  # Language code for OCR (default: eng)
        "webhook_url": "https://example.com/webhook"
    }
    """
    # Inside a route function, we have access to the application context
    queue_task = current_app.queue_task(bypass_queue=False)

    # Define the actual task function
    @queue_task
    def process_extraction(job_id=None, data=None):
        try:
            # Extract parameters
            media_url = data.get("media_url")
            language = data.get("language", "eng")

            # Get supported languages from config
            plugins_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "enabled_plugins.json"
            )
            supported_languages = ["eng"]  # Default fallback

            if os.path.exists(plugins_dir):
                with open(plugins_dir, "r") as f:
                    config = json.load(f)
                    settings = config.get("plugin_settings", {}).get(
                        "text_extraction", {}
                    )
                    supported_languages = settings.get("languages", ["eng"])

            if not media_url:
                return (
                    {"error": "Missing media_url parameter"},
                    "POST /api/extract-text/ocr",
                    400,
                )

            if language not in supported_languages:
                return (
                    {
                        "error": f"Unsupported language '{language}'",
                        "supported_languages": supported_languages,
                    },
                    "POST /api/extract-text/ocr",
                    400,
                )

            # Here you would typically:
            # 1. Download the document
            # 2. Use an OCR library like Tesseract to extract text
            # 3. Return the extracted text

            # For this example, we'll just return a mock response
            result = {
                "media_url": media_url,
                "language": language,
                "text": "This is sample extracted text. In a real implementation, this would be the actual text extracted from the document.",
                "job_id": job_id,
                "confidence": 0.95,
            }

            return result, "POST /api/extract-text/ocr", 200
        except Exception as e:
            return {"error": str(e)}, "POST /api/extract-text/ocr", 500

    # Call the decorated function with the request data
    return process_extraction(data=request.json if request.is_json else {})


@plugin_bp.route("/languages", methods=["GET"])
def get_languages():
    """Return the list of supported languages"""
    # Get supported languages from config
    plugins_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "enabled_plugins.json"
    )
    supported_languages = ["eng"]  # Default fallback

    if os.path.exists(plugins_dir):
        with open(plugins_dir, "r") as f:
            config = json.load(f)
            settings = config.get("plugin_settings", {}).get("text_extraction", {})
            supported_languages = settings.get("languages", ["eng"])

    return jsonify(
        {
            "languages": supported_languages,
            "default": supported_languages[0] if supported_languages else "eng",
        }
    )


def get_blueprint():
    """Return the blueprint for the plugin loader to register"""
    return plugin_bp
