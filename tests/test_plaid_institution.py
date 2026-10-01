from app.plaid import (
    get_plaid_item_institution_name,
)


def test_get_plaid_item_institution_name(
    monkeypatch,
):
    class FakeItem:
        institution_name = "Fairwinds"

    class FakeResponse:
        item = FakeItem()

    class FakeClient:
        def item_get(self, request):
            return FakeResponse()

    result = get_plaid_item_institution_name(
        client=FakeClient(),
        access_token="test-access-token",
    )

    assert result == "Fairwinds"