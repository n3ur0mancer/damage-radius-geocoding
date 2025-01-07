# README: Geospatial Utilities

This repository contains several Python scripts to handle geospatial data processing, focusing on address geocoding, bounding circle calculations, and risk assessment. These tools are designed for applications like locating clients within a specific radius, calculating insured risk amounts, and generating data files (CSV, GeoJSON) for visualization or further analysis.

---

## Files Overview

### **1. address_geocoder.py**
This script provides geocoding and reverse geocoding functionalities. It reads an address dataset and matches addresses or geographic coordinates to specific data points.

**Features:**
- Geocode an address to retrieve its latitude and longitude.
- Reverse geocode latitude and longitude to find the closest address.

**Example Usage:**
```python
geocoder = AddressGeocoder('data/addresses.csv')
result = geocoder.geocode_address('An den Jenken', '69', 'Petange', 4745)
print(result)
```

---

### **2. areal_risk_amount_calculator.py**
Calculates risk amounts within a circular area based on address and client data. It supports geocoding to define the center and filters clients within the specified radius.

**Features:**
- Geocode addresses for circle centers.
- Calculate bounding coordinates for a circular area.
- Filter clients and addresses within the bounding circle.
- Generate a JSON summary of clients and total insured amounts within the circle.

**Example Usage:**
```python
calculator = ArealRiskAmountCalculator(
    bounding_circle_radius_meters=50,
    center_point_address={"street_name": "Rue Michel Rodange", "street_number": "20", "postal_code": 4776}
)
bounding_coordinates = calculator.calculate_bounding_circle()
filtered_addresses = calculator.filter_addresses_in_bounding_circle(bounding_coordinates)
clients_json = calculator.filter_clients_in_bounding_circle(filtered_addresses)
print(clients_json)
```

---

### **3. bounding_circle.py**
A utility script for calculating bounding coordinates of a circle around a geographic point using a radius.

**Features:**
- Compute the latitude and longitude boundaries for a circular area.

**Example Usage:**
```python
circle = BoundingCircle(49.557, 6.033, 100)
bounding_box = circle.bounding_circle()
print(bounding_box)
```

---

### **4. damage_area_geocoder.py**
Combines geocoding and bounding circle calculations to find addresses within a radius and export results as CSV or GeoJSON.

**Features:**
- Find addresses within a specified radius from a central address.
- Export results as CSV or GeoJSON for visualization.

**Example Usage:**
```python
damage_geocoder = DamageAreaGeocoder('data/addresses.csv')
geojson_file = damage_geocoder.get_geojson('Rue Michel Rodange', '20', 4776, 50)
print(f"GeoJSON saved to: {geojson_file}")
```

---

## Setup

### **Prerequisites**
- Python 3.7 or higher
- Required libraries:
  - pandas
  - numpy
  - json
  - math
  - os

### **Installation**
1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/geospatial-utilities.git
   cd geospatial-utilities
   ```
2. Install dependencies:
   ```bash
   pip install pandas numpy
   ```

### **Data Requirements**
- `data/addresses.csv`: Contains address data with columns like `rue`, `numero`, `code_postal`, `lat_wgs84`, and `lon_wgs84`.
- `data/clients.csv`: Contains client data, including address fields (`street_name`, `street_number`, `postal_code`) and `insured_amount_eur`.

---

## Example Data Format

### **addresses.csv**
```csv
rue,numero,code_postal,lat_wgs84,lon_wgs84
"Rue Michel Rodange",20,4776,49.5612,5.8638
```

### **clients.csv**
```csv
street_name,street_number,postal_code,city,insured_amount_eur
"Rue Michel Rodange",20,4776,"Petange",100000
```

---

## Outputs

- **CSV:** Filtered addresses saved as `addresses_in_bounding.csv`.
- **GeoJSON:** Geographic data for visualization saved as `geojson.json`.

