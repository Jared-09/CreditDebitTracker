import os
from decimal import Decimal, ROUND_HALF_UP

import plaid
from dotenv import load_dotenv
from plaid.api import plaid_api


VALID_PLAID_ENVIRONMENTS = {
    "sandbox",
    "production",
}


def get_plaid_config():
    """Load and validate Plaid configuration."""

    load_dotenv()

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