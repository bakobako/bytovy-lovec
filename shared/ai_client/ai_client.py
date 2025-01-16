import re
import json
from rental_ad_schema import validate_property
import google.generativeai as genai
from retry import retry


class AIClient:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    @retry(tries=3, delay=4)
    def _call_gemini_flash(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text

    def turn_response_to_json(self, response):
        try:
            cleaned_response = re.search(r"\{.*\}", response, re.DOTALL)
            if not cleaned_response:
                raise ValueError("No valid JSON found in the response.")

            json_string = cleaned_response.group(0)
            parsed_json = json.loads(json_string)
            validate_property(parsed_json)
            return parsed_json
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse response into JSON: {e}")
        except Exception as e:
            raise ValueError(f"Validation failed: {e}")

    def get_structured_response(self, prompt):
        response_text = self._call_gemini_flash(prompt)
        return self.turn_response_to_json(response_text)

    def analyse_real_estate_ad(self, ad_text):
        prompt = """
        You are an AI assistant specialized in extracting structured data from raw text of real estate listings.
        Your task is to analyze the given raw text from a Czech real estate website and extract specific information 
        into a JSON format.
        Follow these guidelines:
        Extract only the requested information.
        Use the exact key names provided.
        Maintain the original Czech language for extracted values.
        If a piece of information is not available, set the value as None.
        Do not hallucinate any information, if balcony is not mentioned, just keep it None, do not guess.
        Convert numeric values to appropriate data types (e.g., integers for price and area).
        For boolean values, use true or false without quotes.
        Extract and format the following information in JSON:
        {
            "whole_address": complete address of the property, including street and area (string, up to 255 characters),
            "area": general area or district of the property (string, up to 100 characters),
            "street": name of the street where the property is located (string, up to 100 characters),
            "area_m2": area of the apartment in square meters (integer),
            "price_czk": price of the property in Czech koruna (integer) if it is Cena na vyžádání or similar, set it as None,
            "price_per_m2_czk": calculated price per square meter in Czech koruna (integer, generated column),
            "apartment_layout": layout of the apartment, e.g., '2+1' (string, up to 50 characters),
            "number_of_bedrooms": number of bedrooms in the apartment (integer),
            "is_walkthrough_apartment": whether the apartment is a walk-through layout (boolean),
            "floor_number": floor number where the apartment is located (integer),
            "building_floors": total number of floors in the building (integer),
            "ownership": type of ownership, e.g., 'Osobní' (string, up to 50 characters),
            "type_of_building": type of building, e.g., 'Panelová' (string, up to 100 characters),
            "condition": condition of the property, e.g., 'Před rekonstrukcí' (string, up to 100 characters),
            "energy_efficiency_label": energy efficiency rating, e.g., 'A', 'B', 'C' (single character),
            "energy_usage": energy consumption, e.g., '850 kWh/m² rok' (string, up to 50 characters),
            "monthly_payments_czk": monthly payments associated with the property in Czech koruna (integer),
            "is_rooftop_apartment": whether the property is a rooftop apartment (boolean),
            "mezonet": whether the property is a maisonette (boolean),
            "balcony": whether the property has a balcony (boolean),
            "balcony_area_m2": area of the balcony in square meters (integer),
            "terase": whether the property has a terrace (boolean),
            "terase_area_m2": area of the terrace in square meters (integer),
            "parking_spot": whether the property includes a parking spot (boolean),
            "garage": whether the property includes a garage (boolean),
            "elevator": whether the building has an elevator (boolean),
            "cellar": whether the property includes a cellar (boolean),
            "cellar_area_m2": area of the cellar in square meters (integer),
            "flooring_type": type of flooring in the property, e.g., 'Plovoucí podlaha' (string, up to 100 characters),
            "bathroom_layout": layout of the bathroom, e.g., 'Oddělené WC a koupelna' (string, up to 255 characters)
        }
        Respond only with the JSON object. Do not include any additional text or explanations.
        """
        prompt_with_ad = f"{prompt}\n{ad_text}"
        response = self.get_structured_response(prompt_with_ad)
        return response
