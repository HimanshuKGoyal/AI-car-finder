# app/core/logging.py
# Simple structured logger; level depends on debug

import logging
import sys
from app.core.config import settings

logger = logging.getLogger("reco")
logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)
