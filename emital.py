
import sys
if sys.version_info[0] >= 3:  # If using Python 3
    import io
    StringIO = io.StringIO  # Replace StringIO with the correct import

import ee  # Now import ee

import pandas as pd
from predict import predict_label  # Import the predict_label function

json_key_file="new.json"
def authenticate_with_earth_engine(json_key_file):
    try:
        credentials = ee.ServiceAccountCredentials('', json_key_file)
        ee.Initialize(credentials)
        print("Successfully authenticated with Google Earth Engine!")
    except Exception as e:
        print(f"Authentication failed: {e}")

def safe_number(value):
    return value if value is not None else 0

def extract_environmental_data(lat, lon):
    try:
        point = ee.Geometry.Point([lon, lat])
        start_date = '2024-01-01'
        end_date = '2024-12-31'

        s2 = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterDate(start_date, end_date) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))

        def calculate_ndvi(image):
            return image.normalizedDifference(['B8', 'B4']).rename('NDVI')

        def calculate_ndwi(image):
            return image.normalizedDifference(['B3', 'B8']).rename('NDWI')

        def calculate_ndti(image):
            return image.normalizedDifference(['B4', 'B3']).rename('NDTI')

        ndvi = s2.map(calculate_ndvi).mean()
        ndwi = s2.map(calculate_ndwi).mean()
        ndti = s2.map(calculate_ndti).mean()

        elevation = ee.Image('USGS/SRTMGL1_003')
        air_quality = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2') \
            .filterDate(start_date, end_date).mean()
        pm10 = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_AER_AI') \
            .filterDate(start_date, end_date).mean()
        co = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_CO') \
            .filterDate(start_date, end_date).mean()

        def get_value(image, band_name):
            return image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=30,
                maxPixels=1e9
            ).get(band_name).getInfo()

        ndvi_value = safe_number(get_value(ndvi, 'NDVI'))
        ndwi_value = safe_number(get_value(ndwi, 'NDWI'))
        ndti_value = safe_number(get_value(ndti, 'NDTI'))
        elevation_value = safe_number(get_value(elevation, 'elevation'))
        no2_value = safe_number(get_value(air_quality, 'NO2_column_number_density'))
        pm10_value = safe_number(get_value(pm10, 'absorbing_aerosol_index'))
        co_value = safe_number(get_value(co, 'CO_column_number_density'))

        data = {
            "Latitude": lat,
            "Longitude": lon,
            "Label": " ",
            "NDVI": ndvi_value,
            "Vegetation_Index": get_vegetation_description(ndvi_value),
            "NDWI": ndwi_value,
            "NDTI": ndti_value,
            "Land_Elevation": elevation_value,
            "NO2": no2_value,
            "PM10": pm10_value,
            "CO": co_value,
        }

        # Pass the enriched data to the prediction function
        prediction_result = predict_label(data)
        return prediction_result

    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

def get_vegetation_description(ndvi_value):
    if ndvi_value < 0.2:
        return "Bare or sparsely vegetated"
    elif 0.2 <= ndvi_value < 0.5:
        return "Moderate vegetation"
    else:
        return "Dense vegetation"
