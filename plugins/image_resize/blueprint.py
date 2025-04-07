from flask import Blueprint, request, jsonify, current_app
import os
import json

plugin_bp = Blueprint("image_resize", __name__)


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
            settings = config.get("plugin_settings", {}).get("image_resize", {})

    return jsonify(
        {
            "name": "Image Resize Plugin",
            "description": "A plugin for resizing images to custom dimensions",
            "version": "1.0.0",
            "settings": settings,
        }
    )


@plugin_bp.route("/resize", methods=["POST"])
def resize_image():
    """
    Resize an image to the specified dimensions
    Expected JSON payload:
    {
        "image_url": "https://example.com/image.jpg",
        "width": 800,
        "height": 600,
        "preserve_aspect_ratio": true,
        "webhook_url": "https://example.com/webhook"
    }
    """
    # Inside a route function, we have access to the application context
    queue_task = current_app.queue_task(bypass_queue=False)

    # Define the actual task function
    @queue_task
    def process_resize(job_id=None, data=None):
        try:
            # This is a simplified example that would typically use PIL or another
            # image processing library to actually resize the image

            # Extract parameters
            image_url = data.get("image_url")
            width = data.get("width", 800)
            height = data.get("height", 600)

            if not image_url:
                return (
                    {"error": "Missing image_url parameter"},
                    "POST /tools/image-resize/resize",
                    400,
                )

            # Here you would typically:
            # 1. Download the image
            # 2. Resize it with PIL or similar
            # 3. Save the resized image
            # 4. Return the URL to the resized image

            # For this example, we'll just return a mock response
            result = {
                "original_url": image_url,
                "resized_url": f"https://example.com/resized/{job_id}.jpg",
                "width": width,
                "height": height,
                "job_id": job_id,
            }

            return result, "POST /tools/image-resize/resize", 200
        except Exception as e:
            return {"error": str(e)}, "POST /tools/image-resize/resize", 500

    # Call the decorated function with the request data
    return process_resize(data=request.json if request.is_json else {})


def get_blueprint():
    """Return the blueprint for the plugin loader to register"""
    return plugin_bp
