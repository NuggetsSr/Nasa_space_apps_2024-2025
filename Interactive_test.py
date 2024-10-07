import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Step 1: Load your dataset (replace with the correct dataset path)
df = pd.read_csv('Exoplanets Info - Exoplanet_Data_Sorted_by_ESI.csv')

# Step 2: Define the logic to populate the 'Explore' column
# Example rule: if ESI >= 0.9, the exoplanet is a good candidate for exploration
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

# Step 7: Save the trained model for later use
joblib.dump(model, 'exoplanet_explore_model.pkl')

# Step 8: Load the trained model (if needed)
model = joblib.load('exoplanet_explore_model.pkl')

# Step 9: Recommendations for input ranges
recommendations = {
    'ESI': (0.9, 1.0),  # Higher ESI values indicate Earth-like planets
    'Mass (Compared to Jupiter)': (0.1, 1.0),  # Based on training data, smaller masses are preferable
    'Radius compared to Jupiter': (0.1, 1.5),  # Earth-sized planets are likely to be good candidates
    'Magnitude': (10, 16),  # Star magnitude typically falls within this range
    'Distance': (0, 200),  # Focus on nearby planets within 200 light years
    'Incline Angle(deg)': (85, 90)  # Orbital inclinations closer to 90 degrees are better for detection
}

# Display recommended ranges to the user
print("\nRecommended Ranges for Features:")
for feature, (low, high) in recommendations.items():
    print(f"{feature}: {low} - {high}")

# Step 10: Function to take input from the user and predict using the trained model
def get_user_input_and_predict():
    # Collect input for each feature from the user
    user_data = {}
    for feature in feature_names:
        user_data[feature] = float(input(f"Enter value for {feature} (Recommended range {recommendations[feature]}): "))

    # Convert user input into a DataFrame for model prediction
    user_input_df = pd.DataFrame([user_data])

    # Make a prediction using the trained model
    prediction = model.predict(user_input_df)

    # Output the result
    if prediction == 1:
        print("\nPrediction: Explore this exoplanet.")
    else:
        print("\nPrediction: Do not explore this exoplanet.")

# Step 11: Run the function to take user input and make predictions
get_user_input_and_predict()
