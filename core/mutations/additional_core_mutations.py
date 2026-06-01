"""
Additional Core GraphQL Mutations - RefreshTokens, AuditLog
Part of 21-Table Schema Implementation
"""
import strawberry
from typing import Optional
from datetime import datetime
from core.models.core_models import RefreshToken, AuditLog, User
from core.schema.additional_core_schema import RefreshTokenType, AuditLogType, RefreshTokenInput, AuditLogInput


# Response Types
@strawberry.type
class RefreshTokenResponse:
    """Response for RefreshToken mutations"""
    success: bool
    message: str
    token: Optional[RefreshTokenType] = None


@strawberry.type
class AuditLogResponse:
    """Response for AuditLog mutations"""
    success: bool
    message: str
    log: Optional[AuditLogType] = None


# Mutations
@strawberry.type
class RefreshTokenMutations:
    """Mutations for RefreshToken"""
    
    @strawberry.mutation
    def create_refresh_token(self, input: RefreshTokenInput) -> RefreshTokenResponse:
        """Create a new refresh token"""
        try:
            from datetime import datetime
            from django.utils import timezone
            
            user = User.objects.get(user_id=str(input.user_id))
            
            token = RefreshToken.objects.create(
                user=user,
                token_hash=input.token_hash,
                device_info=input.device_info,
                ip_address=input.ip_address,
                expires_at=datetime.fromisoformat(input.expires_at),
            )
            
            return RefreshTokenResponse(
                success=True,
                message="Refresh token created successfully",
                token=RefreshTokenType.from_model(token),
            )
        except User.DoesNotExist:
            return RefreshTokenResponse(
                success=False,
                message="User not found",
            )
        except Exception as e:
            return RefreshTokenResponse(
                success=False,
                message=f"Error creating refresh token: {str(e)}",
            )
    
    @strawberry.mutation
    def revoke_all_sessions(self, user_id: Optional[strawberry.ID] = None) -> RefreshTokenResponse:
        """Revoke all active sessions. If user_id is given, revoke only that user's tokens."""
        try:
            from django.utils import timezone as tz
            qs = RefreshToken.objects.filter(revoked=False, expires_at__gt=tz.now())
            if user_id:
                qs = qs.filter(user_id=user_id)
            count = qs.update(revoked=True)
            scope = f"for user" if user_id else "system-wide"
            return RefreshTokenResponse(success=True, message=f"{count} session(s) revoked {scope}")
        except Exception as e:
            return RefreshTokenResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def revoke_refresh_token(self, token_id: strawberry.ID) -> RefreshTokenResponse:
        """Revoke a refresh token"""
        try:
            token = RefreshToken.objects.get(token_id=str(token_id))
            token.revoked = True
            token.save()
            
            return RefreshTokenResponse(
                success=True,
                message="Refresh token revoked successfully",
                token=RefreshTokenType.from_model(token),
            )
        except RefreshToken.DoesNotExist:
            return RefreshTokenResponse(
                success=False,
                message="Refresh token not found",
            )
        except Exception as e:
            return RefreshTokenResponse(
                success=False,
                message=f"Error revoking refresh token: {str(e)}",
            )


@strawberry.type
class AuditLogMutations:
    """Mutations for AuditLog"""
    
    @strawberry.mutation
    def create_audit_log(self, input: AuditLogInput) -> AuditLogResponse:
        """Create a new audit log entry"""
        try:
            actor = User.objects.get(user_id=str(input.actor_id))
            
            log = AuditLog.objects.create(
                actor=actor,
                action=input.action,
                target_table=input.target_table,
                target_id=str(input.target_id),
                old_value=input.old_value,
                new_value=input.new_value,
                ip_address=input.ip_address,
            )
            
            return AuditLogResponse(
                success=True,
                message="Audit log created successfully",
                log=AuditLogType.from_model(log),
            )
        except User.DoesNotExist:
            return AuditLogResponse(
                success=False,
                message="Actor not found",
            )
        except Exception as e:
            return AuditLogResponse(
                success=False,
                message=f"Error creating audit log: {str(e)}",
            )
