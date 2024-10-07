import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import numpy as np
import matplotlib.pyplot as plt

# Load your dataset
df = pd.read_csv('Exoplanets Info - Exoplanet_Data_Sorted_by_ESI.csv')  # Replace with your dataset path

df= df.fillna(0)

# Define your feature columns and target column
features = ['ESI', 'Mass (Compared to Jupiter)', 'Radius compared to Jupiter', 'Magnitude']
X = df[features]  # Feature set
y = df['Explore']  # Target label (0 or 1 for explore)


# Split the dataset into training and test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.19, random_state=42)

# Print the number of samples in each set
print(f"Training set size: {X_train.shape[0]} samples")
print(f"Test set size: {X_test.shape[0]} samples")

# Train a Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model performance
accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

# Save the trained model to a file
joblib.dump(model, 'exoplanet_explore_model.pkl')

# Load the trained model
model = joblib.load('exoplanet_explore_model.pkl')

# Define the feature names (these should match the features used during training)
feature_names = ['ESI', 'Mass (Compared to Jupiter)', 'Radius compared to Jupiter', 'Magnitude']

# Get the feature importances from the trained model
importances = model.feature_importances_

# Create a DataFrame for visualization
feature_importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
})

# Sort the features by importance
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

# Plot feature importances
plt.figure(figsize=(10, 6))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.xlabel('Feature Importance')
plt.title('Feature Importance for Exoplanet Exploration Model')
plt.gca().invert_yaxis()  # To display the highest importance at the top
plt.show()



