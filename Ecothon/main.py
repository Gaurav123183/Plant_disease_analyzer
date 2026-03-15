from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import base64
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------
# Analyze Plant Image
# -----------------------------
@app.route("/analyze-leaf", methods=["POST"])
def analyze_leaf():

    if "image" not in request.files:
        return jsonify({"result": "No image uploaded"})

    file = request.files["image"]

    image_bytes = file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    image_data = f"data:image/jpeg;base64,{image_base64}"

    prompt = """
Analyze the plant image and return ONLY the information in the following strict format.
Do not add explanations or extra sentences.

Plant Name:
Scientific Name:
Plant Description:
Importance of the Plant:
Water Requirement:
Sunlight Requirement:
Plant Health Status:
Possible Disease Detected:
Risk Percentage:
Symptoms Observed:
Suggested Treatment:
Prevention Tips:

If the image is not a plant return exactly:

Invalid image - please upload a plant image.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data
                            }
                        }
                    ]
                }
            ]
        )

        result = response.choices[0].message.content
        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"result": str(e)})


# -----------------------------
# Manual Plant Info Endpoint
# -----------------------------
@app.route("/plant-info", methods=["POST"])
def plant_info():

    data = request.json
    plant_name = data.get("plantName")

    prompt = f"""
Provide detailed information about the plant: {plant_name}

Return the information in this format:

Plant Name:
Scientific Name:

Plant Description:
(Explain the plant in 3-4 lines)

Importance of the Plant:
(Medicinal, environmental or agricultural importance)

Water Requirement:
Sunlight Requirement:

Common Diseases:

Care Tips:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content
        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"result": str(e)})


if __name__ == "__main__":
    app.run(debug=True)