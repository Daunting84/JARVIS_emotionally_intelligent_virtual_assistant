import torch
import torch.nn as nn
import numpy as np
import joblib

# Model definition (must match training)
class EmotionToPose(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 15)
        )

    def forward(self, x):
        return self.model(x)

# Global vars for reuse
_loaded_model = None
_loaded_scaler = None

# Define lower and upper bounds for each of the 15 output parameters
_lower_bounds = np.array([3.174, -15, 60, -0.782, -13.3, 31, 101, 11.7, 32, 10.5, 35, 0.010, 0.0075, 0.5,1])
_upper_bounds = np.array([7.3, 110, 86.5, 65, 92, -1, 83, -8.6, -14, -10.5, -35, 0.012, 0.009, 1.5, 10])

def neuralnet(avd_values, model_path="emotion2pose.pt", scaler_path="scaler_y.save"):
    """
    Inputs:
      avd_values: list or tuple of 3 floats [Arousal, Valence, Dominance]
      model_path: path to the saved PyTorch model file
      scaler_path: path to the saved output scaler (for inverse transform)

    Returns:
      list of 15 floats - predicted pose parameters (denormalized + clipped)
    """
    global _loaded_model, _loaded_scaler

    # Load model once
    if _loaded_model is None:
        _loaded_model = EmotionToPose()
        _loaded_model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        _loaded_model.eval()

    # Load scaler once
    if _loaded_scaler is None:
        _loaded_scaler = joblib.load(scaler_path)

    # Prepare input
    input_tensor = torch.tensor(avd_values, dtype=torch.float32).unsqueeze(0)  # shape [1, 3]

    # Predict
    with torch.no_grad():
        scaled_output = _loaded_model(input_tensor).numpy()  # Output in normalized form
    output = scaled_output[0].tolist()
    print(scaled_output[0].tolist())
    print(output)

    # Fixing head tilt
    head_tilt_index = 8
    min_val = 32
    max_val = -14
    original_val = output[head_tilt_index]

    flipped_val = min_val + (max_val - original_val)

    # Replace with flipped value
    output[head_tilt_index] = flipped_val

    print("Neural net done")
    print(output[8])

    return output # return as list of 15 floats