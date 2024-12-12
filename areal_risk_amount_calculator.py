import pandas as pd
import numpy as np
import math
import json

# Load Luxembourg addresses as a dataframe and normalize columns
addresses = pd.read_csv("data/addresses.csv", sep=";")
addresses.columns = addresses.columns.str.lower().str.strip()
if 'code_postal' in addresses.columns:
    addresses['code_postal'] = addresses['code_postal'].astype(np.uint16)

# Load mockup clients as a dataframe and normalize columns
clients = pd.read_csv("data/clients.csv", sep=",")
clients.columns = clients.columns.str.lower().str.strip()
if 'postal_code' in clients.columns:
    clients['postal_code'] = clients['postal_code'].astype(np.uint16)


class ArealRiskAmountCalculator:
    def __init__(self, bounding_circle_radius_meters: int, center_point_coordinates: dict = None,
                 center_point_address: dict = None):
        if not (center_point_coordinates or center_point_address):
            raise ValueError("Either 'center_point_coordinates' or 'center_point_address' must be supplied.")
        if center_point_coordinates and center_point_address:
            raise ValueError("Only one of 'center_point_coordinates' or 'center_point_address' should be supplied.")

        self.bounding_circle_radius_meters = bounding_circle_radius_meters
        self.center_point_coordinates = center_point_coordinates
        self.center_point_address = center_point_address

    def geocode_address(self, street_number: str, street_name: str, postal_code: int):
        if not isinstance(postal_code, int):
            raise ValueError("postal_code must be an integer")

        street_name = street_name.lower()
        street_number = str(street_number).lower()

        # Filter by postal code
        filtered_postal_code = addresses[addresses['code_postal'] == postal_code]

        # Match street name
        filtered_street_name = filtered_postal_code[
            filtered_postal_code['rue'].str.lower() == street_name
            ]

        # Match street number
        filtered_street_number = filtered_street_name[
            filtered_street_name['numero'] == street_number
            ]

        if not filtered_street_number.empty:
            result = filtered_street_number.iloc[0][['lat_wgs84', 'lon_wgs84']]
            return {"latitude": float(result['lat_wgs84']), "longitude": float(result['lon_wgs84'])}
        return {"error": "Address not found. Consider fallback to external geocoding."}

    def calculate_min_max_coordinates(self, lat: float, lon: float, radius_meters: int):
        angular_distance = radius_meters / 6371000  # Earth's radius in meters

        # Latitude boundaries (degrees)
        min_lat = lat - math.degrees(angular_distance)
        max_lat = lat + math.degrees(angular_distance)

        # Longitude boundaries (degrees, adjusted for latitude)
        min_lon = lon - math.degrees(angular_distance / math.cos(math.radians(lat)))
        max_lon = lon + math.degrees(angular_distance / math.cos(math.radians(lat)))

        return {
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon
        }

    def calculate_bounding_circle(self):
        if self.center_point_coordinates:
            bounding_coordinates = self.calculate_min_max_coordinates(
                self.center_point_coordinates["latitude"],
                self.center_point_coordinates["longitude"],
                self.bounding_circle_radius_meters
            )
        elif self.center_point_address:
            geocoded_coordinates = self.geocode_address(
                self.center_point_address['street_number'],
                self.center_point_address['street_name'],
                self.center_point_address['postal_code']
            )
            if "error" in geocoded_coordinates:
                raise ValueError(geocoded_coordinates["error"])

            bounding_coordinates = self.calculate_min_max_coordinates(
                geocoded_coordinates["latitude"],
                geocoded_coordinates["longitude"],
                self.bounding_circle_radius_meters
            )
        else:
            raise ValueError("Center point information is missing.")

        return bounding_coordinates


    def filter_addresses_in_bounding_circle(self, bounding_coordinates: dict):
        # Ensure latitude and longitude are numeric
        addresses['lat_wgs84'] = pd.to_numeric(addresses['lat_wgs84'], errors='coerce')
        addresses['lon_wgs84'] = pd.to_numeric(addresses['lon_wgs84'], errors='coerce')

        # Filter addresses within bounding circle
        filtered_bounding_circle_addresses = addresses[
            (addresses['lat_wgs84'] >= bounding_coordinates['min_lat']) &
            (addresses['lat_wgs84'] <= bounding_coordinates['max_lat']) &
            (addresses['lon_wgs84'] >= bounding_coordinates['min_lon']) &
            (addresses['lon_wgs84'] <= bounding_coordinates['max_lon'])
            ]

        return filtered_bounding_circle_addresses


    def filter_clients_in_bounding_circle(self, filtered_bounding_circle_addresses: pd.DataFrame):
        # Ensure postal_code is numeric
        clients['postal_code'] = pd.to_numeric(clients['postal_code'], errors='coerce')
        clients['street_name'] = clients['street_name'].str.lower().str.strip()
        clients['street_number'] = clients['street_number'].astype(str).str.lower().str.strip()

        # Normalize filtered addresses
        filtered_bounding_circle_addresses['rue'] = filtered_bounding_circle_addresses['rue'].str.lower().str.strip()
        filtered_bounding_circle_addresses['numero'] = filtered_bounding_circle_addresses['numero'].astype(
            str).str.lower().str.strip()

        # Merge clients with filtered addresses on matching postal code, street name, and street number
        merged_data = pd.merge(
            clients,
            filtered_bounding_circle_addresses,
            how='inner',
            left_on=['postal_code', 'street_name', 'street_number'],
            right_on=['code_postal', 'rue', 'numero']
        )

        # Prepare the JSON output
        client_list = merged_data.apply(
            lambda row: {
                "client_street_number": row['street_number'],
                "client_street_name": row['street_name'],
                "client_postal_code": row['postal_code'],
                "client_city": row['city'],
                "client_insured_amount_eur": row['insured_amount_eur']
            },
            axis=1
        ).tolist()

        total_insured_amounts_eur = sum(client['client_insured_amount_eur'] for client in client_list)
        # logic to check if either coordinates or address were supplied,
        # if coordinates were supplied but no address -> revers geocode, and take coordinates for circle_center_coordinates
        # if address was supplied -> geocode, and take address for circle_center_street_number, circle_center_street_name, circle_center_postal_code and circle_center_city
        circle_radius_meters = self.bounding_circle_radius_meters

        return json.dumps({"circle_center_coordinates": [],
                           "circle_center_street_number": "",
                           "circle_center_street_name": "",
                           "circle_center_postal_code": "",
                           "circle_center_city": "",
                           "circle_radius_meters": circle_radius_meters,
                           "total_insured_amounts_eur": total_insured_amounts_eur,
                           "clients": client_list},
                          indent=4,
                          ensure_ascii=False)


# Example usage
calculator = ArealRiskAmountCalculator(
    bounding_circle_radius_meters=50,
    center_point_address={
        "street_name": "Rue Michel Rodange",
        "street_number": "20",
        "postal_code": 4776
    }
)

# Step 1: Calculate bounding coordinates
bounding_coordinates = calculator.calculate_bounding_circle()

# Step 2: Filter addresses within the bounding circle
filtered_addresses = calculator.filter_addresses_in_bounding_circle(bounding_coordinates)

# Step 3: Filter clients within the bounding circle and generate JSON
clients_in_bounding_circle_json = calculator.filter_clients_in_bounding_circle(filtered_addresses)

print(clients_in_bounding_circle_json)
