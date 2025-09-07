"""
Module initializing clients that are used globally in the app.
"""

import logging
import os
from typing import Optional

from src.async_module import AsyncClient
from src.email import EmailClient
from src.firebase import FirestoreClient, StorageClient
from src.github import GithubClient
from src.google import GcrClient, SecretClient
from src.payment import StripeClient

logger = logging.getLogger(__name__)

async_client: Optional[AsyncClient] = None
email_client: Optional[EmailClient] = None
firestore_client: Optional[FirestoreClient] = None
gcr_client: Optional[GcrClient] = None
github_client: Optional[GithubClient] = None
secret_client: Optional[SecretClient] = None
storage_client: Optional[StorageClient] = None
stripe_client: Optional[StripeClient] = None


async def initialize_clients_async():
    global \
        async_client, \
        email_client, \
        firestore_client, \
        gcr_client, \
        github_client, \
        secret_client, \
        storage_client, \
        stripe_client

    # Always initialize these core clients
    async_client = AsyncClient()
    github_client = GithubClient()

    # Initialize Firebase clients (required for core functionality)
    try:
        firestore_client = FirestoreClient()
        storage_client = StorageClient()
        logger.info("✅ Firebase clients initialized")
    except Exception as e:
        logger.warning(f"⚠️ Firebase clients failed to initialize: {e}")

    # Initialize email client if API key is available
    if os.getenv("RESEND_API_KEY"):
        try:
            email_client = EmailClient()
            logger.info("✅ Email client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Email client failed to initialize: {e}")
    else:
        logger.info("ℹ️ Email client skipped (no RESEND_API_KEY)")

    # Initialize Stripe client if API key is available
    if os.getenv("STRIPE_SECRET_KEY"):
        try:
            stripe_client = StripeClient()
            logger.info("✅ Stripe client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Stripe client failed to initialize: {e}")
    else:
        logger.info("ℹ️ Stripe client skipped (no STRIPE_SECRET_KEY)")

    # Initialize Google Cloud clients if credentials are available
    try:
        # This will fail if no Google Cloud credentials are found
        secret_client = SecretClient()
        gcr_client = GcrClient()
        logger.info("✅ Google Cloud clients initialized")
    except Exception as e:
        logger.warning(f"Warning: Google Cloud credentials not found, skipping GCP clients: {e}")
        secret_client = None
        gcr_client = None


async def cleanup_clients_async():
    if github_client:
        await github_client.close_async()


def get_async_client() -> AsyncClient:
    if async_client is None:
        raise RuntimeError("Clients not initialized. Call init_clients() first.")
    return async_client


def get_email_client() -> EmailClient:
    if email_client is None:
        raise RuntimeError("Email client not available. Check RESEND_API_KEY environment variable.")
    return email_client


def get_firestore_client() -> FirestoreClient:
    if firestore_client is None:
        raise RuntimeError("Firestore client not initialized. Check Firebase configuration.")
    return firestore_client


def get_gcr_client() -> GcrClient:
    if gcr_client is None:
        raise RuntimeError("Google Cloud Run client not available. Check Google Cloud credentials.")
    return gcr_client


def get_github_client() -> GithubClient:
    if github_client is None:
        raise RuntimeError("GitHub client not initialized. Call init_clients() first.")
    return github_client


def get_secret_client() -> SecretClient:
    if secret_client is None:
        raise RuntimeError("Google Secret Manager client not available. Check Google Cloud credentials.")
    return secret_client


def get_storage_client() -> StorageClient:
    if storage_client is None:
        raise RuntimeError("Firebase Storage client not initialized. Check Firebase configuration.")
    return storage_client


def get_stripe_client() -> StripeClient:
    if stripe_client is None:
        raise RuntimeError("Stripe client not available. Check STRIPE_SECRET_KEY environment variable.")
    return stripe_client
