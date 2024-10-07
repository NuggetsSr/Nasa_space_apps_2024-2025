import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Step 1: Load your dataset (replace with the correct dataset path)
df = pd.read_csv('Exoplanets Info - Exoplanet_Data_Sorted_by_ESI_forAI.csv')

# Step 2: Define the logic to populate the 'Explore' column
df['Explore'] = df['ESI'].apply(lambda x: 1 if x >= 0.9 else 0)

# Step 3: Define your feature columns (now including 'Incline Angle(deg)')
feature_names = ['ESI', 'Mass (Compared to Jupiter)', 'Radius compared to Jupiter', 'Magnitude', 'Distance', 'Incline Angle(deg)']
X = df[feature_names]  # Feature set
y = df['Explore']  # Target label (0 or 1 for explore)

# Step 4: Handle missing values by filling NaN with the mean of each column
X.fillna(X.mean(), inplace=True)

# Step 5: Split the dataset into training (80%) and testing (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 6: Train a Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 7: Save the trained model for later use (optional)
joblib.dump(model, 'exoplanet_explore_model.pkl')

# Step 8: Evaluate the model performance on the test set
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

# Step 9: Get feature importances from the trained model
importances = model.feature_importances_

# Step 10: Create a DataFrame to hold the feature importances for visualization
importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
})

