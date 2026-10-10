import re
import unittest
from pathlib import Path


SCHEMA = (Path(__file__).parents[1] / "supabase_schema.sql").read_text(encoding="utf-8")
SQL = re.sub(r"\s+", " ", SCHEMA.lower())


class SchemaSecurityTests(unittest.TestCase):
    def test_user_tables_enable_row_level_security(self):
        for table in ("profiles", "pipeline"):
            self.assertIn(f"alter table public.{table} enable row level security", SQL)

    def test_every_user_table_operation_is_owner_scoped(self):
        for table in ("profiles", "pipeline"):
            for operation in ("select", "insert", "update", "delete"):
                policy = rf'create policy "{table}_{operation}_own" on public\.{table} for {operation} .*?;'
                match = re.search(policy, SQL)
                self.assertIsNotNone(match, f"missing {operation} policy for {table}")
                self.assertIn("auth.uid() = user_id", match.group())

    def test_owned_rows_are_deleted_with_the_auth_user(self):
        for table in ("profiles", "pipeline"):
            foreign_key = rf"create table if not exists public\.{table} \(.*?references auth\.users\(id\) on delete cascade"
            self.assertRegex(SQL, foreign_key)

    def test_account_deletion_is_authenticated_and_self_scoped(self):
        self.assertIn(
            "function public.delete_my_account() returns void language plpgsql security definer set search_path = ''",
            SQL,
        )
        self.assertIn("if auth.uid() is null then raise exception 'authentication required'", SQL)
        self.assertIn("delete from auth.users where id = auth.uid()", SQL)
        self.assertIn("revoke all on function public.delete_my_account() from public, anon", SQL)
        self.assertIn("grant execute on function public.delete_my_account() to authenticated", SQL)


if __name__ == "__main__":
    unittest.main()
