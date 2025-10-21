"""
Session Management for Shopping Agent

Handles session ID generation and cookie management for persistent carts.
"""

import uuid
from fastapi import Request, Response
from typing import Optional


SESSION_COOKIE_NAME = "pokemon_session_id"
SESSION_MAX_AGE = 86400 * 30  # 30 days in seconds


def get_or_create_session_id(request: Request, response: Response) -> str:
    """
    Get existing session ID from cookie or create new one.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        
    Returns:
        Session ID (UUID string)
    """
    # Try to get existing session ID from cookie
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    
    if not session_id:
        # Generate new session ID
        session_id = str(uuid.uuid4())
        
        # Set cookie in response
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_id,
            max_age=SESSION_MAX_AGE,
            httponly=True,  # Prevent JavaScript access
            samesite="lax",  # CSRF protection
            secure=False,  # Set to True in production with HTTPS
        )
    
    return session_id


def get_session_id(request: Request) -> Optional[str]:
    """
    Get existing session ID from cookie (without creating new one).
    
    Args:
        request: FastAPI request object
        
    Returns:
        Session ID or None if not found
    """
    return request.cookies.get(SESSION_COOKIE_NAME)


def clear_session(response: Response):
    """
    Clear session cookie.
    
    Args:
        response: FastAPI response object
    """
    response.delete_cookie(key=SESSION_COOKIE_NAME)
