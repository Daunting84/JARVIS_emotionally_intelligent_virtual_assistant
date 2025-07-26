import requests
import time
import ast
from neuralnet import neuralnet
from emotion import get_emotion_and_avd
# Converts the list output to pose dict for the API
def nn_output_to_pose_dict(output):
    print("mapping pose")
    return {
        #rotation values being assigned
        "leftShoulderRotate": {"x": output[0], "y": output[1], "z": output[2]},
        "rightShoulderRotate": {"x": output[0], "y": -output[1], "z": -output[2]},
        "leftElbowRotate": {"x": output[3], "y": output[4], "z": output[5]},
        "rightElbowRotate": {"x": output[3], "y": -output[4], "z": -output[5]},
        "Hips": {"x": output[6], "y": 0, "z": 0},
        "Neck": {"x": output[7], "y": 0, "z": 0},
        "Head": {"x": output[8], "y": 0, "z": output[9]},
        "leftWrist": {"x": 14.969, "y": 6.78, "z": output[10]},
        "rightWrist": {"x": 11.1, "y": -5.31, "z": -output[10]},
        #position values being assigned

        "leftPecPos": {"x": -8.881784e-18, "y": 0.011, "z": -1.862645e-11},
        "rightPecPos": {"x": -8.881784e-18, "y": 0.011, "z": -1.862645e-11},
        "leftShoulderPos": {"x": 2.801971e-10, "y": 0.008, "z": -6.984919e-11},
        "rightShoulderPos": {"x": -2.801971e-10, "y": 0.008, "z": -6.984919e-11}
        }


# Sends pose data to the Flask API
def send_pose_update(pose_dict):
    url = 'http://localhost:5000/update_pose'
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, json=pose_dict)
        if response.status_code == 200:
            print('[✓] Pose updated')
        else:
            print(f'[!] Update failed: {response.status_code}')
    except Exception as e:
        print(f'[!] Exception sending update: {e}')


def run_emotion_to_pose(user_text):
    try:
        emotion, my_avd = ast.literal_eval(get_emotion_and_avd(user_text))
        print(f"[→] Detected Emotion: {emotion}, AVD: {my_avd}")
        nn_output = neuralnet(my_avd, model_path=r"C:\Users\nicol\OneDrive\Desktop\Neural Net\ChatModelV1\emotion_to_pose_modelV2.pth")
        pose_data = nn_output_to_pose_dict(nn_output)

        send_pose_update(pose_data)

        time.sleep(0.1)  # Adjust speed as needed (e.g. 0.033 for ~30 FPS)
    except Exception as e:
        print(f"[!] Error in main loop: {e}")
        time.sleep(1)