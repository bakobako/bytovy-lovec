from pydantic import BaseModel, Field, ValidationError
from typing import Optional


class RentalAdSchema(BaseModel):
    whole_address: str = Field(..., description="Complete address of the property.")
    area: str = Field(..., description="General area or district of the property.")
    street: Optional[str] = Field(None, description="Street name where the property is located.")
    area_m2: Optional[float] = Field(..., description="Area of the apartment in square meters.")
    price_czk: Optional[float] = Field(..., description="Price of the property in Czech koruna.")
    price_per_m2_czk: Optional[float] = Field(None,
                                            description="Calculated price per square meter (optional, auto-calculated).")
    apartment_layout: Optional[str] = Field(None, description="Layout of the apartment.")
    number_of_bedrooms: Optional[int] = Field(None, description="Number of bedrooms in the apartment.")
    is_walkthrough_apartment: Optional[bool] = Field(None,
                                                     description="Whether the apartment is a walk-through layout.")
    floor_number: Optional[int] = Field(None, description="Floor number where the apartment is located.")
    building_floors: Optional[int] = Field(None, description="Total number of floors in the building.")
    ownership: Optional[str] = Field(None, description="Type of ownership, e.g., 'Osobní'.")
    type_of_building: Optional[str] = Field(None, description="Type of building, e.g., 'Panelová'.")
    condition: Optional[str] = Field(None, description="Condition of the property.")
    energy_efficiency_label: Optional[str] = Field(None, description="Energy efficiency rating, e.g., 'A', 'B', 'C'.")
    energy_usage: Optional[str] = Field(None, description="Energy consumption, e.g., '850 kWh/m² rok'.")
    monthly_payments_czk: Optional[float] = Field(None, description="Monthly payments associated with the property.")
    is_rooftop_apartment: Optional[bool] = Field(None, description="Whether the property is a rooftop apartment.")
    mezonet: Optional[bool] = Field(None, description="Whether the property is a maisonette.")
    balcony: Optional[bool] = Field(None, description="Whether the property has a balcony.")
    balcony_area_m2: Optional[float] = Field(None, description="Area of the balcony in square meters.")
    terase: Optional[bool] = Field(None, description="Whether the property has a terrace.")
    terase_area_m2: Optional[float] = Field(None, description="Area of the terrace in square meters.")
    parking_spot: Optional[bool] = Field(None, description="Whether the property includes a parking spot.")
    garage: Optional[bool] = Field(None, description="Whether the property includes a garage.")
    elevator: Optional[bool] = Field(None, description="Whether the building has an elevator.")
    cellar: Optional[bool] = Field(None, description="Whether the property includes a cellar.")
    cellar_area_m2: Optional[float] = Field(None, description="Area of the cellar in square meters.")
    flooring_type: Optional[str] = Field(None, description="Type of flooring in the property.")
    bathroom_layout: Optional[str] = Field(None, description="Layout of the bathroom.")


def validate_property(json_data):
    try:
        property_data = RentalAdSchema(**json_data)
        print("Validation successful!")
        return property_data
    except ValidationError as e:
        raise ValueError(f"Validation failed: {e}")
