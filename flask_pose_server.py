from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Updated global in-memory pose data with all relevant parts
pose_data = {
    # Rotations
    "leftShoulderRotate": {"x": 4.944, "y": 4.574, "z": 86.563},
    "rightShoulderRotate": {"x": 4.944, "y": -4.574, "z": -86.563},
    "leftElbowRotate": {"x": -0.782, "y": 0.998, "z": 16.05},
    "rightElbowRotate": {"x": -0.782, "y": -0.782, "z": -16.05},
    "Hips": {"x": 90.34799, "y": 0, "z": 0},
    "Neck": {"x": 0.578, "y": 0, "z": 0},
    "Head": {"x": 6.853, "y": 0, "z": 0},
    "leftWrist": {"x": 14.15, "y": 6.78, "z": 20.586},
    "rightWrist": {"x": 11.124, "y": -5.31, "z": -20.279},

    # Translations
    "leftPecPos": {"x": -8.881784e-18, "y": 0.01067198, "z": -1.862645e-11},
    "rightPecPos": {"x": -8.881784e-18, "y": 0.01067198, "z": -1.862645e-11},
    "leftShoulderPos": {"x": 2.801971e-10, "y": 0.00849444, "z": -6.984919e-11},
    "rightShoulderPos": {"x": -2.793604e-10, "y": 0.008494441, "z": -6.984919e-11},
}

@app.route('/pose', methods=['GET'])
def get_pose():
    return jsonify(pose_data)

@app.route('/update_pose', methods=['POST'])
def update_pose():
    global pose_data
    data = request.get_json()
    print(f"[SERVER] Received data: {data}")
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    for part, values in data.items():
        if part in pose_data and isinstance(values, dict):
            for axis in ['x', 'y', 'z']:
                if axis in values:
                    pose_data[part][axis] = values[axis]

    return jsonify({"status": "success", "pose": pose_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)