import pandas as pd
import numpy as np
import json
import os
import math

# loading Luxembourg addresses as dataframe
addresses = pd.read_csv("data/addresses.csv'", sep=";")
normalized_addresses = addresses.columns.str.lower().str.strip()
if 'code_postal' in normalized_addresses.columns:
    normalized_addresses['code_postal'] = normalized_addresses['code_postal'].astype(np.uint16)

# loading mockup clients as dataframe
clients = pd.read_csv("data/clients.csv'", sep=",")
normalized_clients = clients.columns.str.lower().str.strip()
if 'postal_code' in normalized_clients.columns:
    normalized_clients['postal_code'] = normalized_clients['postal_code'].astype(np.uint16)


class ArealRiskAmountCalculator:
    def __init__(self, bounding_circle_radius_meters: int, center_point_coordinates:tuple=None, center_point_address:dict=None):
        if not (center_point_coordinates or center_point_address):
            raise ValueError("Either 'center_point_coordinates' or 'center_point_address' must be supplied.")
        if center_point_coordinates and center_point_address:
            raise ValueError("Only one of 'center_point_coordinates' or 'center_point_address' should be supplied.")

        self.bounding_circle_radius_meters = bounding_circle_radius_meters
        self.center_point_coordinates = center_point_coordinates
        self.center_point_address = center_point_address


    def calculate_bounding_circle(self, center_point_address: dict, center_point_coordinates: tuple, center_point_radius_meters: int):

        def geocode_address(street_number: str, street_name: str, postal_code: str):
            normalized_street_number = street_number.lower()
            normalized_street_name = street_name.lower()
            assert postal_code is int

            # Filter by postal code
            filtered_postal_code = normalized_addresses[normalized_addresses['code_postal'] == postal_code]

            # Match street name
            filtered_street_name = filtered_postal_code[filtered_postal_code['rue'].str.lower() == normalized_street_name.lower()]

            # Match street number
            filtered_street_number = filtered_street_name[filtered_street_name['numero'] == str(normalized_street_number)]

            if not filtered_street_number.empty:
                result = filtered_street_number.iloc[0][['lat_wgs84', 'lon_wgs84']]
                return {"latitude": float(result['lat_wgs84']), "longitude": float(result['lon_wgs84'])}
            else:
                return {"error": "Address not found. Consider fallback to external geocoding."}


        def calculate_min_max_coordinates(lat: float, lon: float, radius_meters: int):
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

        if center_point_coordinates is None:
            geocoded_coordinates = geocode_address(center_point_address['street_number'],
                                                   center_point_address['street_name'],
                                                   center_point_address['postal_code'])
            bounding_coordinates = calculate_min_max_coordinates(geocoded_coordinates["latitude"],
                                                                 geocoded_coordinates["longitude"],
                                                                 center_point_radius_meters)
            return bounding_coordinates
        else:
            bounding_coordinates = calculate_min_max_coordinates(center_point_coordinates[0],
                                                                 center_point_coordinates[1],
                                                                 center_point_radius_meters)
            return bounding_coordinates


    def filter_addresses_in_bounding_circle(self, ):
        return filtered_bounding_circle_addresses


    def filter_clients_in_bounding_circle(self):
        return filtered_clients_in_bounding_circle_json


    def calculate_total_insurance_amount(self, filtered_clients_json):
        return clients_in_area_with_insurance_amount_json