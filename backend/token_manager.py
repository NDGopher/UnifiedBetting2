#!/usr/bin/env python3
"""
Token Manager for BetBCK JWT Token Extraction
Provides smart token management with expiry detection and refresh capabilities.
"""

import json
import time
import os
from typing import Optional, Dict, Any
from betbck_scraper import extract_jwt_token_from_propbuilder

class TokenManager:
    """Manages JWT tokens with smart caching and expiry detection."""
    
    def __init__(self, cache_file: str = "token_cache.json"):
        self.cache_file = cache_file
        self.cached_tokens = self.load_cache()
    
    def load_cache(self) -> Dict[str, Any]:
        """Load cached tokens from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[TokenManager] Error loading cache: {e}")
        return {}
    
    def save_cache(self):
        """Save tokens to cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cached_tokens, f, indent=2)
        except Exception as e:
            print(f"[TokenManager] Error saving cache: {e}")
    
    def is_token_valid(self, token_data: Dict[str, Any]) -> bool:
        """Check if a token is still valid (not expired)."""
        if not token_data:
            return False
        
        extracted_at = token_data.get('extracted_at', 0)
        expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
        
        # Check if token has expired (with 5 minute buffer)
        time_since_extraction = time.time() - extracted_at
        return time_since_extraction < (expires_in - 300)  # 5 min buffer
    
    def get_valid_token(self) -> Optional[Dict[str, Any]]:
        """Get a valid token from cache if available."""
        token_data = self.cached_tokens.get('betbck_token')
        
        if self.is_token_valid(token_data):
            print(f"[TokenManager] Using cached token (age: {int((time.time() - token_data['extracted_at']) / 60)} minutes)")
            return token_data
        
        print("[TokenManager] No valid cached token available")
        return None
    
    def refresh_token(self) -> Optional[Dict[str, Any]]:
        """Extract a fresh token from BetBCK."""
        print("[TokenManager] Extracting fresh token from BetBCK...")
        
        try:
            token_data = extract_jwt_token_from_propbuilder()
            
            if token_data:
                # Cache the new token
                self.cached_tokens['betbck_token'] = token_data
                self.save_cache()
                
                print(f"[TokenManager] Fresh token extracted and cached")
                return token_data
            else:
                print("[TokenManager] Failed to extract token")
                return None
                
        except Exception as e:
            print(f"[TokenManager] Error during token extraction: {e}")
            return None
    
    def get_token(self, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a token - use cached if valid, otherwise extract fresh.
        
        Args:
            force_refresh: If True, always extract a fresh token
        """
        if force_refresh:
            return self.refresh_token()
        
        # Try cached token first
        valid_token = self.get_valid_token()
        if valid_token:
            return valid_token
        
        # No valid cached token, extract fresh
        return self.refresh_token()
    
    def is_token_expired_error(self, error_response: str) -> bool:
        """
        Check if an API error indicates token expiry.
        
        Args:
            error_response: Error response from bet placement API
        """
        expired_indicators = [
            'unauthorized',
            'token expired',
            'invalid token',
            'authentication failed',
            '401',
            'forbidden',
            '403'
        ]
        
        error_lower = error_response.lower()
        return any(indicator in error_lower for indicator in expired_indicators)
    
    def handle_api_error(self, error_response: str) -> Optional[Dict[str, Any]]:
        """
        Handle API error and refresh token if needed.
        
        Args:
            error_response: Error response from API
            
        Returns:
            Fresh token if error was due to expiry, None otherwise
        """
        if self.is_token_expired_error(error_response):
            print("[TokenManager] API error suggests token expiry, refreshing...")
            return self.refresh_token()
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current token status."""
        token_data = self.cached_tokens.get('betbck_token')
        
        if not token_data:
            return {
                'has_token': False,
                'is_valid': False,
                'age_minutes': 0,
                'expires_in_minutes': 0
            }
        
        age_seconds = time.time() - token_data.get('extracted_at', 0)
        age_minutes = int(age_seconds / 60)
        expires_in_seconds = token_data.get('expires_in', 3600) - age_seconds
        expires_in_minutes = max(0, int(expires_in_seconds / 60))
        
        return {
            'has_token': True,
            'is_valid': self.is_token_valid(token_data),
            'age_minutes': age_minutes,
            'expires_in_minutes': expires_in_minutes,
            'user': token_data.get('user', 'unknown'),
            'token_preview': token_data.get('token', '')[:20] + '...'
        }

# Global token manager instance
token_manager = TokenManager()
