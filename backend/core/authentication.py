from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django_redis import get_redis_connection
from rest_framework_simplejwt.utils import aware_utcnow
import json

class RedisTokenStore:
    """Custom token store using Redis for JWT tokens"""
    
    def __init__(self):
        self.redis_conn = get_redis_connection("default")
        self.token_prefix = "jwt:token:"
        self.blacklist_prefix = "jwt:blacklist:"
    
    def add_token(self, user_id, jti, token_data, expires_at):
        """Store a token in Redis"""
        # Convert datetime to timestamp for Redis storage
        exp_timestamp = int(expires_at.timestamp())
        
        # Store token data with expiration
        token_key = f"{self.token_prefix}{jti}"
        data = {
            "user_id": user_id,
            "jti": jti,
            "token_data": token_data,
            "expires_at": exp_timestamp,
            "created_at": int(aware_utcnow().timestamp())
        }
        
        # Store in Redis with expiration time
        self.redis_conn.set(
            token_key, 
            json.dumps(data),
            ex=int((expires_at - aware_utcnow()).total_seconds())
        )
        
        # Also store in a user's token list
        user_tokens_key = f"jwt:user:{user_id}:tokens"
        self.redis_conn.sadd(user_tokens_key, jti)
        
        return True
    
    def blacklist_token(self, jti):
        """Blacklist a token"""
        # Check if token exists
        token_key = f"{self.token_prefix}{jti}"
        token_data = self.redis_conn.get(token_key)
        
        if not token_data:
            return False
        
        # Add to blacklist
        blacklist_key = f"{self.blacklist_prefix}{jti}"
        token_data = json.loads(token_data)
        
        # Calculate remaining time for expiration
        expires_at = token_data.get("expires_at", 0)
        now = int(aware_utcnow().timestamp())
        ttl = max(0, expires_at - now)
        
        # Store in blacklist with same expiration as original token
        self.redis_conn.set(blacklist_key, "1", ex=ttl)
        
        return True
    
    def is_blacklisted(self, jti):
        """Check if a token is blacklisted"""
        blacklist_key = f"{self.blacklist_prefix}{jti}"
        return bool(self.redis_conn.exists(blacklist_key))

class RedisJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication that uses Redis for token verification and blacklist checking"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_store = RedisTokenStore()
    
    def get_validated_token(self, raw_token):
        """
        Validates a token and returns its payload.
        Adds Redis blacklist verification.
        """
        # Get the validated token from parent method
        token = super().get_validated_token(raw_token)
        
        # Check if the token is blacklisted in Redis
        jti = token.get('jti')
        if jti and self.token_store.is_blacklisted(jti):
            raise InvalidToken('Token is blacklisted')
        
        return token