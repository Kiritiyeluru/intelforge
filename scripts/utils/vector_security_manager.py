#!/usr/bin/env python3
"""
Vector Security Manager for IntelForge
Provides security enhancements for vector storage operations including
authentication, encryption, audit logging, and access control
"""

import base64
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Security configuration for vector storage"""

    encryption_enabled: bool = True
    audit_logging_enabled: bool = True
    authentication_enabled: bool = True
    access_control_enabled: bool = True
    audit_log_path: str = "logs/vector_security_audit.log"
    secret_key_path: str = "config/vector_security.key"


class VectorSecurityManager:
    """Manages security aspects of vector storage operations"""

    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.session_id = hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]
        self._setup_logging()
        self._setup_encryption()

    def _setup_logging(self):
        """Setup audit logging for vector operations"""
        if not self.config.audit_logging_enabled:
            return

        # Create logs directory if it doesn't exist
        log_dir = Path(self.config.audit_log_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Setup audit logger
        self.audit_logger = logging.getLogger("vector_security_audit")
        self.audit_logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if not self.audit_logger.handlers:
            handler = logging.FileHandler(self.config.audit_log_path)
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)

    def _setup_encryption(self):
        """Setup encryption key for vector data"""
        if not self.config.encryption_enabled:
            self.cipher_suite = None
            return

        key_path = Path(self.config.secret_key_path)

        # Create config directory if it doesn't exist
        key_path.parent.mkdir(parents=True, exist_ok=True)

        if key_path.exists():
            # Load existing key
            with open(key_path, "rb") as f:
                key = f.read()
        else:
            # Generate new key
            password = os.environ.get(
                "VECTOR_ENCRYPTION_PASSWORD", "default_password"
            ).encode()
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))

            # Save key securely
            with open(key_path, "wb") as f:
                f.write(key)

            # Set restrictive permissions
            os.chmod(key_path, 0o600)

        self.cipher_suite = Fernet(key)

    def encrypt_vector_data(self, data: bytes) -> bytes:
        """Encrypt vector data if encryption is enabled"""
        if not self.config.encryption_enabled or not self.cipher_suite:
            return data

        try:
            encrypted_data = self.cipher_suite.encrypt(data)
            self.log_security_event(
                "ENCRYPTION", "Vector data encrypted", {"data_size": len(data)}
            )
            return encrypted_data
        except Exception as e:
            self.log_security_event(
                "ENCRYPTION_ERROR", f"Encryption failed: {str(e)}", {"error": str(e)}
            )
            raise

    def decrypt_vector_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt vector data if encryption is enabled"""
        if not self.config.encryption_enabled or not self.cipher_suite:
            return encrypted_data

        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            self.log_security_event(
                "DECRYPTION",
                "Vector data decrypted",
                {"data_size": len(decrypted_data)},
            )
            return decrypted_data
        except Exception as e:
            self.log_security_event(
                "DECRYPTION_ERROR", f"Decryption failed: {str(e)}", {"error": str(e)}
            )
            raise

    def validate_vector_payload(self, payload: Dict[str, Any]) -> bool:
        """Validate vector payload for security threats"""
        try:
            # Check for oversized payloads
            payload_size = len(json.dumps(payload))
            if payload_size > 10 * 1024 * 1024:  # 10MB limit
                self.log_security_event(
                    "VALIDATION_FAILED", "Payload too large", {"size": payload_size}
                )
                return False

            # Check for malicious content patterns
            payload_str = json.dumps(payload)
            suspicious_patterns = [
                "<script",
                "<?php",
                "{{",
                "${",
                "eval(",
                "exec(",
                "__import__",
                "subprocess",
                "os.system",
            ]

            for pattern in suspicious_patterns:
                if pattern in payload_str.lower():
                    self.log_security_event(
                        "VALIDATION_FAILED",
                        f"Suspicious pattern detected: {pattern}",
                        {"pattern": pattern},
                    )
                    return False

            # Validate embedding dimensions if present
            if "embedding" in payload:
                embedding = payload["embedding"]
                if isinstance(embedding, list) and len(embedding) > 0:
                    if len(embedding) > 2048:  # Reasonable embedding size limit
                        self.log_security_event(
                            "VALIDATION_FAILED",
                            "Embedding too large",
                            {"size": len(embedding)},
                        )
                        return False

                    # Check for malformed embeddings
                    if not all(isinstance(x, (int, float)) for x in embedding):
                        self.log_security_event(
                            "VALIDATION_FAILED", "Invalid embedding format", {}
                        )
                        return False

            self.log_security_event(
                "VALIDATION_SUCCESS",
                "Payload validation passed",
                {"size": payload_size},
            )
            return True

        except Exception as e:
            self.log_security_event(
                "VALIDATION_ERROR", f"Validation error: {str(e)}", {"error": str(e)}
            )
            return False

    def log_security_event(
        self, event_type: str, message: str, metadata: Dict[str, Any] = None
    ):
        """Log security events for audit trail"""
        if not self.config.audit_logging_enabled:
            return

        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "message": message,
            "session_id": self.session_id,
            "metadata": metadata or {},
        }

        self.audit_logger.info(json.dumps(audit_entry))

    def log_vector_operation(
        self,
        operation: str,
        collection: str,
        metadata: Dict[str, Any] = None,
        user: str = "system",
    ):
        """Log vector database operations"""
        if not self.config.audit_logging_enabled:
            return

        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "VECTOR_OPERATION",
            "operation": operation,
            "collection": collection,
            "user": user,
            "session_id": self.session_id,
            "metadata": metadata or {},
        }

        self.audit_logger.info(json.dumps(audit_entry))

    def check_access_permissions(
        self, user: str, operation: str, collection: str
    ) -> bool:
        """Check if user has permission for the requested operation"""
        if not self.config.access_control_enabled:
            return True

        # Basic role-based access control
        # This should be extended with a proper user management system
        user_roles = {
            "admin": ["read", "write", "delete", "create"],
            "read_write": ["read", "write"],
            "read_only": ["read"],
            "system": ["read", "write", "delete", "create"],
        }

        # Default role assignment (should be configured properly)
        user_role = "system"  # Default for now

        allowed_operations = user_roles.get(user_role, [])

        if operation.lower() in allowed_operations:
            self.log_security_event(
                "ACCESS_GRANTED",
                f"Access granted for {operation}",
                {"user": user, "operation": operation, "collection": collection},
            )
            return True
        else:
            self.log_security_event(
                "ACCESS_DENIED",
                f"Access denied for {operation}",
                {"user": user, "operation": operation, "collection": collection},
            )
            return False

    def generate_api_key(self, user: str, permissions: List[str]) -> str:
        """Generate API key for user with specific permissions"""
        key_data = {
            "user": user,
            "permissions": permissions,
            "created_at": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
        }

        # Generate key from user data
        key_string = json.dumps(key_data, sort_keys=True)
        api_key = hashlib.sha256(key_string.encode()).hexdigest()

        self.log_security_event(
            "API_KEY_GENERATED",
            f"API key generated for user {user}",
            {"user": user, "permissions": permissions},
        )

        return api_key

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return user info"""
        # This is a simplified implementation
        # In production, this should check against a secure key store
        self.log_security_event(
            "API_KEY_VALIDATION",
            "API key validation requested",
            {"key_hash": hashlib.sha256(api_key.encode()).hexdigest()[:16]},
        )

        # For now, return basic system permissions
        return {
            "user": "system",
            "permissions": ["read", "write", "delete", "create"],
            "valid": True,
        }

    def sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata to remove sensitive information"""
        sanitized = {}

        # List of sensitive keys to remove or mask
        sensitive_keys = [
            "password",
            "token",
            "key",
            "secret",
            "api_key",
            "auth",
            "credential",
            "private",
            "confidential",
        ]

        for key, value in metadata.items():
            key_lower = key.lower()

            # Check if key contains sensitive information
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
                self.log_security_event(
                    "METADATA_SANITIZED",
                    f"Sensitive key sanitized: {key}",
                    {"key": key},
                )
            else:
                sanitized[key] = value

        return sanitized

    def get_security_health_check(self) -> Dict[str, Any]:
        """Perform security health check"""
        health_status = {
            "encryption": {
                "enabled": self.config.encryption_enabled,
                "status": "healthy" if self.cipher_suite else "disabled",
            },
            "audit_logging": {
                "enabled": self.config.audit_logging_enabled,
                "status": "healthy" if self.audit_logger else "disabled",
            },
            "access_control": {
                "enabled": self.config.access_control_enabled,
                "status": "basic" if self.config.access_control_enabled else "disabled",
            },
            "key_management": {
                "key_file_exists": Path(self.config.secret_key_path).exists(),
                "status": (
                    "configured"
                    if Path(self.config.secret_key_path).exists()
                    else "not_configured"
                ),
            },
        }

        self.log_security_event(
            "HEALTH_CHECK", "Security health check performed", health_status
        )
        return health_status


# Global security manager instance
security_manager = VectorSecurityManager()
