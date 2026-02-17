import numpy as np
from controllers.input_handler import InputHandler
from models.ann import ANN

class InteractionController:
    """
    Manages the interaction between the touchpad input and the neural network system.
    """

    def __init__(self, neural_net_model, input_dim=(28, 28)):
        """
        Initializes the InteractionController.
        
        Args:
            neural_net_model (NeuralNet): Trained neural network model for inference.
            input_dim (tuple): Dimensions of the processed input data.
        """
        self.input_handler = InputHandler(input_dim=input_dim)
        self.model = neural_net_model
        self.data_point = np.zeros((50,50)) #initialize data point
        self.raw_data_buffer = []

    def collect_raw_data(self, position):
        x, y, pressure = position
        if 0 <= y < self.data_point.shape[0] and 0 <= x < self.data_point.shape[1]:
            self.data_point[y, x] = pressure  # Mark the interaction point
        else:
            print(f"Warning: Position ({x}, {y}) is out of bounds.")

    def preprocess_and_infer(self):
        """
        Processes the collected data and performs inference using the neural network.
        
        Returns:
            int: Predicted label from the neural network.
        """
        if not self.raw_data_buffer:
            print("No data collected.")
            return None

        # Combine raw data into a single array (e.g., summing pressure points)
        combined_data = np.sum(self.raw_data_buffer, axis=0)

        # Preprocess the input data
        processed_input = self.input_handler.preprocess_input(combined_data)
        input_vector = self.input_handler.get_input_vector(processed_input)

        # Perform inference
        prediction = self.model.predict(input_vector)
        return prediction

    def reset_interaction(self):
        """
        Resets the raw data buffer to prepare for a new interaction.
        """
        self.raw_data_buffer = []

# Example Usage
if __name__ == "__main__":
    # Simulating a pretrained neural network
    class DummyNeuralNet:
        def predict(self, input_vector):
            return np.argmax(np.random.rand(10))  # Random digit prediction (0-9)

    # Initialize components
    neural_net = DummyNeuralNet()
    interaction = InteractionController(neural_net_model=neural_net)

    # Simulate touchpad events
    interaction.collect_raw_data((25, 25, 100))  # Touch at (25, 25) with pressure 100
    interaction.collect_raw_data((30, 30, 150))  # Touch at (30, 30) with pressure 150

    # Process and infer
    predicted_label = interaction.preprocess_and_infer()
    print("Predicted Label:", predicted_label)

    # Reset for the next interaction
    interaction.reset_interaction()
