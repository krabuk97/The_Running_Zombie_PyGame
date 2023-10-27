from django.conf import settings

COMMENT_PLACEHOLDER = getattr(settings, "COMMENT_PLACEHOLDER", "Be nice.")
COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 3000)
