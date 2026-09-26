import unittest
from unittest.mock import MagicMock, patch

from tradara_cloud import TradaraCloud


class CloudSessionTests(unittest.TestCase):
    @patch("tradara_cloud.create_client")
    def test_visitors_receive_distinct_auth_clients(self, create_client):
        first_client, second_client = MagicMock(), MagicMock()
        create_client.side_effect = [first_client, second_client]

        first = TradaraCloud("https://example.supabase.co", "public-anon-key")
        second = TradaraCloud("https://example.supabase.co", "public-anon-key")
        first.sign_in("first@example.com", "password")

        self.assertIs(first.client, first_client)
        self.assertIs(second.client, second_client)
        first_client.auth.sign_in_with_password.assert_called_once()
        second_client.auth.sign_in_with_password.assert_not_called()

    @patch("tradara_cloud.create_client")
    def test_account_deletion_uses_user_scoped_rpc(self, create_client):
        cloud = TradaraCloud("https://example.supabase.co", "public-anon-key")
        cloud.delete_account()
        create_client.return_value.rpc.assert_called_once_with("delete_my_account")


if __name__ == "__main__":
    unittest.main()
