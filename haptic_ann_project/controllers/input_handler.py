import numpy as np

class InputHandler:
    """
    Handles raw input data from the touchpad and processes it for use in the neural network.
    """

    def __init__(self, input_dim=(28, 28)):
        """
        Initializes the InputHandler with the required input dimensions.
        
        Args:
            input_dim (tuple): The dimensions of the input image (default is 28x28 for digits).
        """
        self.input_dim = input_dim

    def normalize_data(self, data):
        """
        Normalizes the raw data to the range [0, 1].
        
        Args:
            data (numpy.ndarray): Raw data from the touchpad.
        
        Returns:
            numpy.ndarray: Normalized data.
        """
        return data / 255.0

    def resize_data(self, data):
        """
        Resizes the input data to match the neural network's expected input dimensions.
        
        Args:
            data (numpy.ndarray): Raw input data.
        
        Returns:
            numpy.ndarray: Resized data.
        """
        return np.resize(data, self.input_dim)

    def preprocess_input(self, raw_data):
        """
        Processes the raw input data: normalization and resizing.
        
        Args:
            raw_data (numpy.ndarray): Raw input data from the touchpad.
        
        Returns:
            numpy.ndarray: Preprocessed input data.
        """
        normalized_data = self.normalize_data(raw_data)
        resized_data = self.resize_data(normalized_data)
        return resized_data

    def get_input_vector(self, preprocessed_data):
        """
        Converts the preprocessed data into a flat vector for the neural network.
        
        Args:
            preprocessed_data (numpy.ndarray): Preprocessed data.
        
        Returns:
            numpy.ndarray: Flattened data vector.
        """
        return preprocessed_data.flatten()

# Example Usage
if __name__ == "__main__":
    # Simulating raw data from the touchpad (e.g., 50x50 grayscale)
    raw_input = np.random.randint(0, 256, (50, 50))
    
    handler = InputHandler(input_dim=(28, 28))
    processed_input = handler.preprocess_input(raw_input)
    input_vector = handler.get_input_vector(processed_input)
    
    print("Processed Input Shape:", processed_input.shape)
    print("Input Vector Shape:", input_vector.shape)
