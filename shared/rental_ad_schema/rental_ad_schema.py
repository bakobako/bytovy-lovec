from typing import Optional
from pydantic import BaseModel, Field, ValidationError


class RentalAdSchema(BaseModel):
    property_type: str = Field(..., description="Type of property (e.g., 'Apartment').")
    listing_price: float = Field(..., description="Price of the property in Czech koruna.")
    currency: str = Field(..., description="Currency of the listing price.")
    city: str = Field(..., description="City where the property is located.")
    district: Optional[str] = Field(None, description="District where the property is located.")
    street: Optional[str] = Field(None, description="Street name where the property is located.")
    house_number: Optional[str] = Field(None, description="House number of the property.")
    latitude: Optional[float] = Field(None, description="Latitude coordinates of the property.")
    longitude: Optional[float] = Field(None, description="Longitude coordinates of the property.")
    num_bedrooms: Optional[int] = Field(None, description="Number of bedrooms in the property.")
    num_bathrooms: Optional[int] = Field(None, description="Number of bathrooms in the property.")
    area_m2: Optional[float] = Field(None, description="Total area of the property in square meters.")
    apartment_layout: Optional[str] = Field(None, description="Layout of the apartment.")
    is_walkthrough_apartment: Optional[bool] = Field(None, description="Whether the apartment has a walk-through layout.")
    floor_number: Optional[int] = Field(None, description="Floor number where the apartment is located.")
    building_floors: Optional[int] = Field(None, description="Total number of floors in the building.")
    type_of_ownership: Optional[str] = Field(None, description="Type of ownership, e.g., 'Osobní'.")
    type_of_building: Optional[str] = Field(None, description="Type of building, e.g., 'Panelová'.")
    condition: Optional[str] = Field(None, description="Condition of the property.")
    energy_efficiency_label: Optional[str] = Field(None, description="Energy efficiency rating, e.g., 'A', 'B', 'C'.")
    energy_usage: Optional[str] = Field(None, description="Energy consumption, e.g., '850 kWh/m² rok'.")  # Kept as VARCHAR
    monthly_payments_czk: Optional[float] = Field(None, description="Monthly payments associated with the property.")
    is_rooftop_apartment: Optional[bool] = Field(None, description="Whether the property is a rooftop apartment.")
    is_mezonet: Optional[bool] = Field(None, description="Whether the property is a maisonette.")
    has_balcony: Optional[bool] = Field(None, description="Whether the property has a balcony.")
    balcony_area_m2: Optional[float] = Field(None, description="Area of the balcony in square meters.")
    has_terrace: Optional[bool] = Field(None, description="Whether the property has a terrace.")
    terrace_area_m2: Optional[float] = Field(None, description="Area of the terrace in square meters.")
    has_parking_spot: Optional[bool] = Field(None, description="Whether the property includes a parking spot.")
    has_garage: Optional[bool] = Field(None, description="Whether the property includes a garage.")
    has_elevator: Optional[bool] = Field(None, description="Whether the building has an elevator.")
    has_cellar: Optional[bool] = Field(None, description="Whether the property includes a cellar.")
    cellar_area_m2: Optional[float] = Field(None, description="Area of the cellar in square meters.")
    flooring_type: Optional[str] = Field(None, description="Type of flooring in the property.")


def validate_property(json_data):
    try:
        property_data = RentalAdSchema(**json_data)
        print("Validation successful!")
        return property_data
    except ValidationError as e:
        raise ValueError(f"Validation failed: {e}")
