import pandas as pd
import numpy as np

class AddressGeocoder:
    def __init__(self, csv_file, delimiter=';'):
        """
        Initialize the geocoder with the address data.
        """
        self.addresses = pd.read_csv(csv_file, sep=delimiter)
        # Normalize column names
        self.addresses.columns = self.addresses.columns.str.lower().str.strip()
        # Optimize the datatype for code_postal
        if 'code_postal' in self.addresses.columns:
            self.addresses['code_postal'] = self.addresses['code_postal'].astype(np.uint16)
    
    def geocode_address(self, rue: str, numero: str, localite:str , code_postal: int):
        """
        Geocode the given address by matching fields in the dataset.
        
        :param rue: Street name
        :param numero: Street number
        :param localite: Locality (city)
        :param code_postal: Postal code (ZIP code)
        :return: Dictionary with latitude and longitude or error message
        """
        # Filter by ZIP code
        filtered_zip = self.addresses[self.addresses['code_postal'] == code_postal]
        
        # Match street name, normalize to lower case
        filtered_street = filtered_zip[filtered_zip['rue'].str.lower() == rue.lower()]
        
        # Match street number, use strig because number can include letters
        filtered_number = filtered_street[filtered_street['numero'] == str(numero)]
        
        if not filtered_number.empty:
            result = filtered_number.iloc[0][['lat_wgs84', 'lon_wgs84']]
            return {"latitude": float(result['lat_wgs84']), "longitude": float(result['lon_wgs84'])}
        else:
            return {"error": "Address not found. Consider fallback to external geocoding."}
    
    def reverse_geocode_address(self, latitude: float, longitude: float):
        """
        Reverse geocode the given latitude and longitude to find the closest address.
        
        :param latitude: Latitude of the location
        :param longitude: Longitude of the location
        :return: Dictionary with the closest address or error message
        """
        # Calculate the Euclidean distance to each address
        self.addresses['distance'] = np.sqrt(
            (self.addresses['lat_wgs84'] - latitude) ** 2 +
            (self.addresses['lon_wgs84'] - longitude) ** 2
        )
        
        closest_address = self.addresses.loc[self.addresses['distance'].idxmin()]
        
        return {
            "numero": closest_address['numero'],
            "rue": closest_address['rue'],
            "localite": closest_address['localite'],
            "code_postal": int(closest_address['code_postal']),
        }


# Example Usage
if __name__ == "__main__":
    geocoder = AddressGeocoder('data/addresses.csv')

    geocode_result = geocoder.geocode_address(
        numero='69',
        rue='An den Jenken',
        localite='Petange',
        code_postal=4745
    )

    reverse_geocode_result = geocoder.reverse_geocode_address(
        latitude=49.5620012, 
        longitude=5.863799)

    print("-------------------------------------------")
    print("Geocode Result:", geocode_result)
    print("Reverse Geocode Result:", reverse_geocode_result)
    print("-------------------------------------------")
