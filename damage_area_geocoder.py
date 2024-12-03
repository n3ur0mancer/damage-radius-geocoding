import pandas as pd
from address_geocoder import AddressGeocoder
from bounding_circle import BoundingCircle
import json
import os

class DamageAreaGeocoder:
    def __init__(self, csv_file, delimiter=';'):
        """
        Initialize the DamageAreaGeocoder with the CSV file containing addresses.
        """
        self.geocoder = AddressGeocoder(csv_file, delimiter)
        self.addresses = pd.read_csv(csv_file, sep=delimiter)
        self.addresses.columns = self.addresses.columns.str.lower().str.strip()

    def get_addresses_within_radius(self, rue: str, numero: str, code_postal: int, radius_meters: int):
        """
        Find addresses within a given radius from the provided address.
        """
        # Geocode the center address
        geocode_result = self.geocoder.geocode_address(rue, numero, None, code_postal)
        
        # Check if the geocoding was successful
        if 'error' in geocode_result:
            return geocode_result

        latitude = geocode_result['latitude']
        longitude = geocode_result['longitude']

        # Compute the bounding circle around the center address
        bounding_circle = BoundingCircle(center_lat=latitude, center_lon=longitude, radius_meters=radius_meters)
        bounding = bounding_circle.bounding_circle()

        # Filter the addresses within the bounding circle
        filtered_addresses = self.addresses[
            (self.addresses['lat_wgs84'] >= bounding['min_lat']) &
            (self.addresses['lat_wgs84'] <= bounding['max_lat']) &
            (self.addresses['lon_wgs84'] >= bounding['min_lon']) &
            (self.addresses['lon_wgs84'] <= bounding['max_lon'])
        ]

        return filtered_addresses
    

    def get_csv(self, rue: str, numero: str, code_postal: int, radius_meters: int, output_dir='data'):
        """
        Get filtered addresses within the radius, 
        then save it to a CSV file in the specified directory.
        """
        addresses_within_bounding = self.get_addresses_within_radius(rue, numero, code_postal, radius_meters)
        
        if 'error' in addresses_within_bounding:
            return addresses_within_bounding

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        csv_file_path = os.path.join(output_dir, 'addresses_in_bounding.csv')

        addresses_within_bounding.to_csv(csv_file_path, index=False)

        return csv_file_path


    def get_geojson(self, rue: str, numero: str, code_postal: int, radius_meters: int, output_dir='data'):
        """
        Get filtered addresses within the radius, 
        then save the GeoJSON to a file in the specified directory.
        """
        addresses_within_bounding = self.get_addresses_within_radius(rue, numero, code_postal, radius_meters)
        
        if 'error' in addresses_within_bounding:
            return addresses_within_bounding
        
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        for _, address in addresses_within_bounding.iterrows():
            filtered_address = self.addresses[
                (self.addresses['rue'].str.lower() == address['rue'].lower()) &
                (self.addresses['numero'] == str(address['numero'])) &
                (self.addresses['code_postal'] == address['code_postal'])
            ].iloc[0]

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(filtered_address['lon_wgs84']), 
                        float(filtered_address['lat_wgs84']) 
                    ]
                },
                "properties": {
                    "rue": filtered_address['rue'],
                    "numero": filtered_address['numero'],
                    "code_postal": int(filtered_address['code_postal'])
                }
            }
            geojson["features"].append(feature)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        geojson_file_path = os.path.join(output_dir, 'geojson.json')
        with open(geojson_file_path, 'w') as geojson_file:
            json.dump(geojson, geojson_file, indent=4)

        return geojson_file_path


# Example usage
if __name__ == "__main__":
    damage_geocoder = DamageAreaGeocoder('data/addresses.csv')

    user_input = {
        "rue": "Rue Michel Rodange",
        "numero": "20",
        "code_postal": 4776,
        "radius_meters": 50
    }

    print("-------------------------------------------")
    csv_file = damage_geocoder.get_csv(
        rue=user_input['rue'],
        numero=user_input['numero'],
        code_postal=user_input['code_postal'],
        radius_meters=user_input['radius_meters']
    )
    print(f"Filtered addresses saved to CSV: {csv_file}")

    geojson_file = damage_geocoder.get_geojson(
        rue=user_input['rue'],
        numero=user_input['numero'],
        code_postal=user_input['code_postal'],
        radius_meters=user_input['radius_meters']
    )
    print(f"GeoJSON saved to: {geojson_file}")
    print("-------------------------------------------")
