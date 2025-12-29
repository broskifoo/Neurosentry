# [DETECTOR / ASSISTANT]
# This script uses SHAP and feature importance to explain our baseline model.

import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt

def main():
    """ Load the model and data, then generate and save explanation plots. """
    print("Loading model and data...")
    
    # 1. Load Model and Data
    try:
        model = joblib.load('baseline_model.joblib')
        df = pd.read_csv('features.csv')
    except FileNotFoundError as e:
        print(f"[ERROR] Could not find file: {e.filename}")
        print("Please ensure 'baseline_model.joblib' and 'features.csv' exist.")
        return

    # Separate features (X) and labels (y)
    X = df.drop('label', axis=1)
    y = df['label']

    print("Model and data loaded successfully.")

    # --- 2. Simple Feature Importance (from RandomForest) ---
    print("\n--- Simple Feature Importance ---")
    
    # Get importance scores from the trained model
    importances = model.feature_importances_
    
    # Create a simple table of feature names and their scores
    feature_importance_df = pd.DataFrame({
        'feature': X.columns,
        'importance': importances
    }).sort_values(by='importance', ascending=False)
    
    print(feature_importance_df.head(10))

    # --- 3. Advanced SHAP Explanation ---
    print("\nCalculating SHAP values... This may take a moment.")
    
    # Create a SHAP explainer object for our tree-based model
    explainer = shap.TreeExplainer(model)
    
    # Calculate SHAP values for all our data
    # shap_values[1] corresponds to the "malicious" class (label=1)
    shap_values = explainer.shap_values(X)

    # Create a summary plot (a bar chart)
    # This shows the average impact of each feature on the model's output
    print("Generating SHAP summary plot...")
    plt.figure() # Create a new plot
    shap.summary_plot(shap_values, X, plot_type="bar", show=False)
    
    # Save the plot to a file
    plot_filename = 'shap_summary_plot.png'
    plt.savefig(plot_filename, bbox_inches='tight')
    
    print(f"\nSHAP summary plot saved as '{plot_filename}'")
    print("This plot shows the features with the highest average impact on the model's decision.")

if __name__ == "__main__":
    main()