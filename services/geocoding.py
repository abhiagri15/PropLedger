"""
Geocoding service for address lookup and validation
Uses OpenStreetMap's Nominatim service (free) as primary, with Google Places as fallback
"""

import requests
import json
from typing import List, Dict, Optional
import streamlit as st
from config import get_openai_api_key

class GeocodingService:
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.google_places_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        self.google_geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.openai_api_key = get_openai_api_key()
    
    def search_addresses(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Search for addresses using multiple services
        Returns list of address suggestions with formatted addresses
        """
        if not query or len(query.strip()) < 3:
            return []
        
        suggestions = []
        
        # Try OpenStreetMap Nominatim first (free)
        try:
            nominatim_results = self._search_nominatim(query, limit)
            suggestions.extend(nominatim_results)
        except Exception as e:
            st.warning(f"OpenStreetMap service unavailable: {str(e)}")
        
        # If we have Google API key, try Google Places
        if self.openai_api_key and len(suggestions) < limit:
            try:
                google_results = self._search_google_places(query, limit - len(suggestions))
                suggestions.extend(google_results)
            except Exception as e:
                st.warning(f"Google Places service unavailable: {str(e)}")
        
        # Remove duplicates and return
        unique_suggestions = []
        seen_addresses = set()
        
        for suggestion in suggestions:
            if suggestion['address'] not in seen_addresses:
                unique_suggestions.append(suggestion)
                seen_addresses.add(suggestion['address'])
                
                if len(unique_suggestions) >= limit:
                    break
        
        return unique_suggestions
    
    def _search_nominatim(self, query: str, limit: int) -> List[Dict[str, str]]:
        """Search using OpenStreetMap Nominatim (free service)"""
        params = {
            'q': query,
            'format': 'json',
            'limit': limit,
            'addressdetails': 1,
            'countrycodes': 'us,ca,gb,au',  # Focus on major English-speaking countries
            'dedupe': 1
        }
        
        headers = {
            'User-Agent': 'PropLedger/1.0 (Property Management System)'
        }
        
        response = requests.get(self.nominatim_url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        
        results = response.json()
        suggestions = []
        
        for result in results:
            address_parts = result.get('address', {})
            
            # Build formatted address
            formatted_address = self._format_nominatim_address(result, address_parts)
            
            suggestions.append({
                'address': formatted_address,
                'display_name': result.get('display_name', ''),
                'lat': result.get('lat', ''),
                'lon': result.get('lon', ''),
                'source': 'OpenStreetMap'
            })
        
        return suggestions
    
    def _search_google_places(self, query: str, limit: int) -> List[Dict[str, str]]:
        """Search using Google Places API (requires API key)"""
        if not self.openai_api_key:
            return []
        
        # Note: This would require Google Places API key
        # For now, return empty list as we don't have Google API key
        return []
    
    def _format_nominatim_address(self, result: Dict, address_parts: Dict) -> str:
        """Format address from Nominatim result"""
        # Extract key components
        house_number = address_parts.get('house_number', '')
        road = address_parts.get('road', '')
        city = address_parts.get('city', '') or address_parts.get('town', '') or address_parts.get('village', '')
        state = address_parts.get('state', '') or address_parts.get('province', '')
        postcode = address_parts.get('postcode', '')
        country = address_parts.get('country', '')
        
        # Build address components
        street_address = f"{house_number} {road}".strip()
        
        # Create formatted address
        address_components = []
        
        if street_address:
            address_components.append(street_address)
        if city:
            address_components.append(city)
        if state:
            address_components.append(state)
        if postcode:
            address_components.append(postcode)
        if country and country not in ['United States', 'Canada', 'United Kingdom', 'Australia']:
            address_components.append(country)
        
        return ', '.join(address_components)
    
    def get_address_details(self, address: str) -> Optional[Dict[str, str]]:
        """Get detailed address information including coordinates"""
        try:
            coords = self.get_coordinates(address)
            if coords:
                return {
                    'address': address,
                    'lat': coords['lat'],
                    'lon': coords['lon'],
                    'map_url': f"https://www.google.com/maps?q={coords['lat']},{coords['lon']}"
                }
        except Exception as e:
            st.warning(f"Could not get address details: {str(e)}")
        
        return None
    
    def get_coordinates(self, address: str) -> Optional[Dict[str, float]]:
        """Get latitude and longitude for an address"""
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'PropLedger/1.0 (Property Management System)'
            }
            
            response = requests.get(self.nominatim_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            
            results = response.json()
            if results:
                return {
                    'lat': float(results[0].get('lat', 0)),
                    'lon': float(results[0].get('lon', 0))
                }
        except Exception as e:
            st.warning(f"Could not get coordinates for address: {str(e)}")
        
        return None

# Global instance
geocoding_service = GeocodingService()
