from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)

from app.database import initialize_database

from app.plaid import (
    create_link_token,
    create_plaid_client,
    exchange_public_token,
    get_plaid_account_balances,
    get_plaid_item_institution_name,
)

from app.plaid_account_registration import (
    register_plaid_accounts,
)

from app.plaid_items import (
    save_plaid_item,
)


app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "plaid_link.html"
    )


@app.route(
    "/api/create_link_token",
    methods=["POST"],
)
def api_create_link_token():

    client = create_plaid_client()

    link_token = create_link_token(
        client=client,
    )

    return jsonify(
        {
            "link_token": link_token,
        }
    )


@app.route(
    "/api/exchange_public_token",
    methods=["POST"],
)
def api_exchange_public_token():

    data = request.get_json()

    if not data:
        return jsonify(
            {
                "error": "Request body is required."
            }
        ), 400

    public_token = data.get(
        "public_token"
    )

    if not public_token:
        return jsonify(
            {
                "error": "public_token is required."
            }
        ), 400

    client = create_plaid_client()

    result = exchange_public_token(
        client=client,
        public_token=public_token,
    )

    save_plaid_item(
        item_id=result["item_id"],
        access_token=result["access_token"],
    )

    institution_name = (
        get_plaid_item_institution_name(
            client=client,
            access_token=result["access_token"],
        )
    )

    plaid_accounts = (
        get_plaid_account_balances(
            client=client,
            access_token=result["access_token"],
        )
    )

    register_plaid_accounts(
        item_id=result["item_id"],
        plaid_accounts=plaid_accounts,
        institution_name=institution_name,
    )

    return jsonify(
        {
            "success": True,
            "item_id": result["item_id"],
        }
    )


def run():

    initialize_database()

    print()
    print("================================")
    print("Credit Card Control - Plaid Link")
    print("================================")
    print()

    print(
        "Open this address in your browser:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    print(
        "Press CTRL+C to stop the server."
    )

    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )


if __name__ == "__main__":
    run()