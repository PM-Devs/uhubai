from joblib import load

def predict_label(new_data):
    """
    Predict the label for new data using the trained CatBoost model.
    
    Args:
        new_data (dict): A dictionary with keys matching the dataset's features.

    Returns:
        str: The predicted label.
    """
    # Load the saved model
    model = load("catboost_emit_model.joblib")

    # Expected feature order (consistent with training)
    feature_order = ['NDVI', 'NDWI', 'NDTI', 'NO2', 'Land_Elevation',
                   'Vegetation_Index_Encoded', 'PM10', 'CO']
    
    # Encode 'Vegetation_Index' to its numeric value
    vegetation_mapping = {
        "Bare or sparsely vegetated": 0,
        "Moderate vegetation": 1,
        "Dense vegetation": 2
    }
    # Add 'Vegetation_Index_Encoded' based on the mapping
    new_data['Vegetation_Index_Encoded'] = vegetation_mapping.get(new_data.get('Vegetation_Index', ''), -1)

    # Validate that all expected features are present
    missing_features = [feature for feature in feature_order if feature not in new_data]
    if missing_features:
        raise ValueError(f"Missing expected feature(s) in new_data: {missing_features}")

    # Ensure the input data is in the correct order
    input_data = [[new_data[feature] for feature in feature_order]]

    # Make prediction
    prediction = model.predict(input_data)
    return prediction[0]
