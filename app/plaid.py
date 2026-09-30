import os
from decimal import Decimal, ROUND_HALF_UP

import plaid
from dotenv import load_dotenv
from plaid.api import plaid_api
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import (
    SandboxPublicTokenCreateRequest,
)


# Load local environment variables once when this module is imported.
# Existing environment variables are not overwritten.
load_dotenv()


VALID_PLAID_ENVIRONMENTS = {
    "sandbox",
    "production",
}


def get_plaid_config():
    """Read and validate Plaid configuration."""

    client_id = os.getenv("PLAID_CLIENT_ID")
    secret = os.getenv("PLAID_SECRET")
    environment = os.getenv(
        "PLAID_ENV",
        "sandbox",
    ).lower()

    if not client_id:
        raise ValueError(
            "PLAID_CLIENT_ID is not configured."
        )

    if not secret:
        raise ValueError(
            "PLAID_SECRET is not configured."
        )

    if environment not in VALID_PLAID_ENVIRONMENTS:
        raise ValueError(
            f"Invalid PLAID_ENV: {environment}"
        )

    return {
        "client_id": client_id,
        "secret": secret,
        "environment": environment,
    }


def create_plaid_client():
    """Create a configured Plaid API client."""

    config = get_plaid_config()

    if config["environment"] == "sandbox":
        host = plaid.Environment.Sandbox
    else:
        host = plaid.Environment.Production

    configuration = plaid.Configuration(
        host=host,
        api_key={
            "clientId": config["client_id"],
            "secret": config["secret"],
        },
    )

    api_client = plaid.ApiClient(
        configuration
    )

    return plaid_api.PlaidApi(
        api_client
    )


def create_sandbox_public_token(client):
    """Create a Transactions Item in Plaid Sandbox."""

    request = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",
        initial_products=[
            Products("transactions"),
        ],
    )

    response = client.sandbox_public_token_create(
        request
    )

    return response.public_token


def exchange_public_token(
    client,
    public_token,
):
    """Exchange a Plaid public token for an access token."""

    request = ItemPublicTokenExchangeRequest(
        public_token=public_token,
    )

    response = client.item_public_token_exchange(
        request
    )

    return {
        "access_token": response.access_token,
        "item_id": response.item_id,
    }


def normalize_plaid_amount(plaid_amount):
    """
    Convert a signed Plaid amount into the positive
    magnitude used by the internal accounting engine.
    """

    amount = Decimal(str(plaid_amount)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    return float(abs(amount))


def classify_plaid_transaction(
    plaid_amount,
    primary_category=None,
):
    """
    Classify a Plaid credit-card transaction for the
    internal accounting engine.
    """

    amount = Decimal(str(plaid_amount))

    if amount >= Decimal("0"):
        return "purchase"

    if primary_category == "LOAN_PAYMENTS":
        return "payment"

    return "refund"


def convert_plaid_transaction(plaid_transaction):
    """
    Convert a raw Plaid transaction into the format
    expected by the application's sync system.
    """

    personal_finance_category = plaid_transaction.get(
        "personal_finance_category"
    )

    primary_category = None

    if personal_finance_category is not None:
        primary_category = personal_finance_category.get(
            "primary"
        )

    plaid_amount = plaid_transaction["amount"]

    return {
        "plaid_transaction_id": plaid_transaction[
            "transaction_id"
        ],
        "pending_transaction_id": plaid_transaction.get(
            "pending_transaction_id"
        ),
        "merchant_name": plaid_transaction.get(
            "merchant_name"
        ),
        "description": plaid_transaction.get(
            "name"
        ),
        "transaction_date": plaid_transaction[
            "date"
        ],
        "plaid_amount": normalize_plaid_amount(
            plaid_amount
        ),
        "pending": plaid_transaction["pending"],
        "transaction_type": classify_plaid_transaction(
            plaid_amount=plaid_amount,
            primary_category=primary_category,
        ),
    }