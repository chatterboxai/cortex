from typing import List
import logging

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse

from app.auth.cognito import extract_token_from_header
from app.auth.cognito import verify_cognito_token
from cognitojwt import CognitoJWTException

logger = logging.getLogger(__name__)


class CognitoAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for validating AWS Cognito JWT tokens.
    """
    
    def __init__(
        self,
        app,
        exclude_paths: List[str] = None,
        exclude_methods: List[str] = None,
    ):
        """
        Initialize the middleware.
        
        Args:
            app: The FastAPI application
            exclude_paths: List of paths to exclude from authentication
            exclude_methods: List of HTTP methods to exclude from
                authentication
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.exclude_methods = exclude_methods or []
        
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request and validate JWT token if required.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler
            
        Returns:
            The response from the next middleware or endpoint
        """
        # Skip authentication for excluded paths and methods
        path = request.url.path
        method = request.method
        
        if path in self.exclude_paths or method in self.exclude_methods:
            return await call_next(request)
            
        # Get token from header
        auth_header = request.headers.get('Authorization')
        token = extract_token_from_header(auth_header)
        
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Missing authentication token'},
            )
            
        try:
            # Verify and decode the token
            claims = await verify_cognito_token(token)
            
            request.state.claims = claims

            return await call_next(request)
            
        except CognitoJWTException as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': e.args},
            )
        except Exception as e:
            logger.exception(f'Unexpected error in auth middleware: {e}')
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    'detail': 'Internal server error during authentication'
                },
            )
