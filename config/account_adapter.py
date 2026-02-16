"""Custom allauth adapter hooks."""

import logging
from typing import Iterable

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


class GobiiAccountAdapter(DefaultAccountAdapter):
    """Reject signups that use a blocked email domain or aren't in allowed list."""

    def clean_email(self, email: str) -> str:
        cleaned_email = super().clean_email(email)
        domain = cleaned_email.rsplit("@", 1)[-1].lower()

        # Check blocked domains first
        blocked_domain = self._match_blocked_domain(
            domain, getattr(settings, "SIGNUP_BLOCKED_EMAIL_DOMAINS", ())
        )
        if blocked_domain:
            logger.warning(
                "Signup rejected for blocked email domain",
                extra={"domain": blocked_domain},
            )
            raise ValidationError(
                f"We can't create accounts with email addresses from {blocked_domain}. "
                "Please use a different email."
            )

        # If allowed emails list is configured, enforce it
        allowed_emails = getattr(settings, "SIGNUP_ALLOWED_EMAILS", None)
        if allowed_emails:
            email_lower = cleaned_email.lower()
            if email_lower not in [e.lower() for e in allowed_emails]:
                logger.warning(
                    "Signup rejected for email not in allowed list",
                    extra={"email": cleaned_email},
                )
                raise ValidationError(
                    "Signups are restricted. Please contact the administrator."
                )

        return cleaned_email

    @staticmethod
    def _match_blocked_domain(domain: str, blocked_domains: Iterable[str] | None) -> str | None:
        if not blocked_domains:
            return None

        for blocked in blocked_domains:
            if domain == blocked or domain.endswith(f".{blocked}"):
                return blocked

        return None
