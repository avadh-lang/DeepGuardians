"""
Random Forest Model for Parking Availability Classification
Classifies parking availability into categories: abundant, available, limited, critical
"""
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import numpy as np


def build_parking_rf(n_estimators=200, max_depth=20, random_state=42):
    """
    Build Random Forest classifier for parking availability
    
    Args:
        n_estimators: number of trees
        max_depth: maximum depth of trees
        random_state: random seed
    
    Returns:
        RandomForestClassifier
    """
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=10,
        min_samples_leaf=4,
        max_features='sqrt',
        random_state=random_state,
        n_jobs=-1,  # Use all CPU cores
        verbose=1
    )
    
    return model


def get_feature_importance(model, feature_names):
    """
    Get feature importance from trained model
    """
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    print("\nFeature Importance:")
    print("=" * 50)
    for i, idx in enumerate(indices[:10]):  # Top 10 features
        print(f"{i+1}. {feature_names[idx]}: {importances[idx]:.4f}")
    
    return list(zip(feature_names, importances))


def save_rf_model(model, path="../../models/parking_rf_model.pkl"):
    """Save Random Forest model"""
    joblib.dump(model, path)
    print(f"✓ Random Forest model saved to {path}")


def load_rf_model(path="../../models/parking_rf_model.pkl"):
    """Load Random Forest model"""
    return joblib.load(path)


if __name__ == "__main__":
    # Test model creation
    model = build_parking_rf()
    print("✓ Random Forest model created successfully")
    print(f"  - Trees: {model.n_estimators}")
    print(f"  - Max Depth: {model.max_depth}")
