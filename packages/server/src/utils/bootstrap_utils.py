import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app

from src.clients import initialize_clients_async

logger = logging.getLogger(__name__)


@dataclass
class BootstrapConfig:
    log_level: int = logging.INFO
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    firebase_cert_path: str = "async-firebase.json"
    load_env: bool = True
    initialize_firebase: bool = True
    initialize_clients: bool = True


async def bootstrap_application_async(config: BootstrapConfig = BootstrapConfig()) -> None:
    if config.load_env:
        load_dotenv()

    logging.basicConfig(
        level=config.log_level,
        format=config.log_format,
    )

    if config.initialize_firebase:
        try:
            if os.path.exists(config.firebase_cert_path):
                cred = credentials.Certificate(config.firebase_cert_path)
                initialize_app(cred)
                logger.info("✅ Firebase Admin initialized")
            else:
                logger.warning(f"⚠️ Firebase certificate not found: {config.firebase_cert_path}")
        except Exception as e:
            logger.warning(f"⚠️ Firebase initialization failed: {e}")

    if config.initialize_clients:
        await initialize_clients_async()


def create_bootstrap_config(is_dev: bool = False) -> BootstrapConfig:
    return BootstrapConfig(log_level=logging.DEBUG if is_dev else logging.INFO)
