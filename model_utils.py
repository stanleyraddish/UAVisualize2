from keras.models import model_from_json

# Loads model from .json file for model struct and .h5 file for weights
def load_network_from_json_and_h5(struct_json_path, weights_path):
    with open(struct_json_path, 'r') as json_file:
        model_json = json_file.read()

    # Load model from json file
    model = model_from_json(model_json)

    # Load weights to model
    model.load_weights(weights_path)

    return model