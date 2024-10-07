import pandas as pd
import joblib

# Load the trained model
model = joblib.load('exoplanet_explore_model.pkl')

# Unseen data (replace this with actual unseen data)
# Ensure that this data has the same feature columns as the data you trained the model on.
unseen_data = pd.DataFrame({
    'ESI': [1, 0.65, 0.90],  # Replace with actual data
    'Mass (Compared to Jupiter)': [1.1, 0.9, 0.5],
    'Radius compared to Jupiter': [1.2, 0.8, 0.9],
    'Magnitude': [12.1, 13.5, 11.7]
})

# Make predictions using the trained model
predictions = model.predict(unseen_data)

# Print the predictions (1 = Explore, 0 = Not Explore)
for i, pred in enumerate(predictions):
    status = 'Explore' if pred == 1 else 'Not Explore'
    print(f"Exoplanet {i + 1}: {status}")
