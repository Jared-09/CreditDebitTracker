from plaid.model.transactions_sync_request import (
    TransactionsSyncRequest,
)


def sync_transactions(
    client,
    access_token,
    cursor=None,
):
    """
    Run a Plaid transactions/sync request.

    cursor=None means this is the first sync.
    A cursor value means continue from the previous sync.
    """

    request = TransactionsSyncRequest(
        access_token=access_token,
    )

    if cursor:
        request.cursor = cursor

    response = client.transactions_sync(
        request
    )

    return {
        "added": response.added,
        "modified": response.modified,
        "removed": response.removed,
        "next_cursor": response.next_cursor,
    }