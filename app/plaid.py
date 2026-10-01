import os
from decimal import Decimal, ROUND_HALF_UP

import plaid
from dotenv import load_dotenv
from plaid.api import plaid_api
from plaid.model.accounts_balance_get_request import (
    AccountsBalanceGetRequest,
)
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import (
    LinkTokenCreateRequest,
)
from plaid.model.link_token_create_request_user import (
    LinkTokenCreateRequestUser,
)
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import (
    SandboxPublicTokenCreateRequest,
)


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


def create_link_token(
    client,
    client_user_id="credit-card-control-user",
):
    """
    Create a Plaid Link token for connecting a
    financial institution.
    """

    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(
            client_user_id=client_user_id,
        ),
        client_name="Credit Card Control",
        products=[
            Products("transactions"),
        ],
        country_codes=[
            CountryCode("US"),
        ],
        language="en",
    )

    response = client.link_token_create(
        request
    )

    return response.link_token


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


def get_plaid_account_balances(
    client,
    access_token,
):
    """
    Retrieve current and available balances for all
    accounts belonging to a Plaid Item.
    """

    request = AccountsBalanceGetRequest(
        access_token=access_token,
    )

    response = client.accounts_balance_get(
        request
    )

    accounts = getattr(
        response,
        "accounts",
        None,
    )

    if not isinstance(
        accounts,
        (list, tuple),
    ):
        accounts = []

    balances = []

    for account in accounts:
        current_balance = account.balances.current
        available_balance = account.balances.available

        balances.append(
            {
                "plaid_account_id": account.account_id,
                "name": account.name,
                "official_name": account.official_name,
                "mask": getattr(
                    account,
                    "mask",
                    None,
                ),
                "account_type": str(
                    account.type
                ),
                "account_subtype": str(
                    account.subtype
                ),
                "current_balance": (
                    float(current_balance)
                    if current_balance is not None
                    else None
                ),
                "available_balance": (
                    float(available_balance)
                    if available_balance is not None
                    else None
                ),
            }
        )

    return balances


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


def convert_plaid_transaction(
    plaid_transaction,
):
    """
    Convert a raw Plaid transaction into the format
    expected by the application's sync system.
    """

    personal_finance_category = plaid_transaction.get(
        "personal_finance_category"
    )

    primary_category = None

    if personal_finance_category is not None:
        primary_category = (
            personal_finance_category.get(
                "primary"
            )
        )

    plaid_amount = plaid_transaction["amount"]

    return {
        "plaid_transaction_id": (
            plaid_transaction["transaction_id"]
        ),
        "pending_transaction_id": (
            plaid_transaction.get(
                "pending_transaction_id"
            )
        ),
        "merchant_name": (
            plaid_transaction.get(
                "merchant_name"
            )
        ),
        "description": (
            plaid_transaction.get("name")
        ),
        "transaction_date": (
            plaid_transaction["date"]
        ),
        "plaid_amount": normalize_plaid_amount(
            plaid_amount
        ),
        "pending": plaid_transaction["pending"],
        "transaction_type": classify_plaid_transaction(
            plaid_amount=plaid_amount,
            primary_category=primary_category,
        ),
    }