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

    def test_business_values_are_enforced_at_the_database_boundary(self):
        self.assertIn("constraint profiles_non_negative_values check", SQL)
        for column in ("max_distance_km", "min_job_value", "max_job_value", "revenue_target"):
            self.assertIn(f"{column} >= 0", SQL)
        self.assertIn("constraint profiles_valid_job_range check (min_job_value <= max_job_value)", SQL)
        self.assertIn("constraint pipeline_non_negative_est_value check (est_value >= 0)", SQL)
        self.assertIn("length(btrim(development)) > 0", SQL)
        self.assertIn("length(btrim(trade)) > 0", SQL)

    def test_integrity_constraints_are_safe_to_rerun(self):
        self.assertEqual(SQL.count("exception when duplicate_object then null"), 4)

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
