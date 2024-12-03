import math

class BoundingCircle:
    EARTH_RADIUS = 6371000  # Earth's radius in meters

    def __init__(self, center_lat, center_lon, radius_meters):
        """
        Initialize the BoundingCircle object with center coordinates and radius.

        :param center_lat: Latitude of the center point in degrees
        :param center_lon: Longitude of the center point in degrees
        :param radius_meters: Radius in meters
        """
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_meters = radius_meters

    def bounding_circle(self):
        """
        Compute the bounding box for a circle with a given radius around a central coordinate.

        :return: Dictionary with lat/lon boundaries (min_lat, max_lat, min_lon, max_lon)
        """
        angular_distance = self.radius_meters / self.EARTH_RADIUS

        # Latitude boundaries (degrees)
        min_lat = self.center_lat - math.degrees(angular_distance)
        max_lat = self.center_lat + math.degrees(angular_distance)

        # Longitude boundaries (degrees, adjusted for latitude)
        min_lon = self.center_lon - math.degrees(angular_distance / math.cos(math.radians(self.center_lat)))
        max_lon = self.center_lon + math.degrees(angular_distance / math.cos(math.radians(self.center_lat)))

        return {
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon
        }

# Example usage
if __name__ == "__main__":
    center = {"latitude": 49.557, "longitude": 6.033}
    radius = 100

    bounding_circle = BoundingCircle(center_lat=center["latitude"], center_lon=center["longitude"], radius_meters=radius)
    bounding_box = bounding_circle.bounding_circle()
    print("-------------------------------------------")
    print("Bounding Circle")
    print("Min. Latitude:", bounding_box["min_lat"])
    print("Max. Latitude:", bounding_box["max_lat"])
    print("Min. Longitude:", bounding_box["min_lon"])
    print("Max. Longitude:", bounding_box["max_lon"])
    print("-------------------------------------------")
