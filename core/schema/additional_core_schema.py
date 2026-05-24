"""
Additional Core GraphQL Schema Types - RefreshTokens, AuditLog
Part of 21-Table Schema Implementation
"""
import strawberry
from typing import Optional
from core.models.core_models import RefreshToken, AuditLog


@strawberry.type
class RefreshTokenType:
    """GraphQL type for RefreshToken"""
    id: strawberry.ID
    user_id: strawberry.ID
    token_hash: str
    device_info: Optional[str]
    ip_address: Optional[str]
    issued_at: str
    expires_at: str
    revoked: bool
    
    @classmethod
    def from_model(cls, token: RefreshToken) -> 'RefreshTokenType':
        return cls(
            id=str(token.token_id),
            user_id=str(token.user.user_id),
            token_hash=token.token_hash,
            device_info=token.device_info,
            ip_address=token.ip_address,
            issued_at=token.issued_at.isoformat(),
            expires_at=token.expires_at.isoformat(),
            revoked=token.revoked,
        )


@strawberry.type
class AuditLogType:
    """GraphQL type for AuditLog"""
    id: strawberry.ID
    actor_id: strawberry.ID
    action: str
    target_table: str
    target_id: str
    old_value: Optional[str]
    new_value: Optional[str]
    ip_address: Optional[str]
    performed_at: str
    
    @classmethod
    def from_model(cls, log: AuditLog) -> 'AuditLogType':
        return cls(
            id=str(log.log_id),
            actor_id=str(log.actor.user_id),
            action=log.action,
            target_table=log.target_table,
            target_id=str(log.target_id),
            old_value=str(log.old_value) if log.old_value else None,
            new_value=str(log.new_value) if log.new_value else None,
            ip_address=log.ip_address,
            performed_at=log.performed_at.isoformat(),
        )


# Input Types
@strawberry.input
class RefreshTokenInput:
    """Input for creating RefreshToken"""
    user_id: strawberry.ID
    token_hash: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: str


@strawberry.input
class AuditLogInput:
    """Input for creating AuditLog"""
    actor_id: strawberry.ID
    action: str
    target_table: str
    target_id: strawberry.ID
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
