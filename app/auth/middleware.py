from typing import List
import logging

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse

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
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.exclude_methods = exclude_methods or []
        
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip authentication for excluded paths and methods
        path = request.url.path
        method = request.method
        
        if path in self.exclude_paths or method in self.exclude_methods:
            return await call_next(request)
            
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Missing authentication token'},
            )

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Invalid authentication token'},
            )

        token = parts[1]
        
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Missing authentication token'},
            )
            
        try:
            claims = await verify_cognito_token(token)
            
            # Store the claims in request state for use in dependencies
            request.state.claims = claims

            return await call_next(request)
            
        except CognitoJWTException as e:
            logger.warning(f'JWT validation failed: {str(e)}')
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    'detail': 'Invalid or expired authentication token'
                },
            )
        except Exception as e:
            logger.exception(f'Unexpected error in auth middleware: {e}')
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    'detail': 'Internal server error during authentication'
                },
            )
