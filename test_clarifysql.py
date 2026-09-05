import unittest

from clarification import check_clarification

from conversation_manager import ConversationManager

from sql_generator import (
    validate_user_request,
    validate_sql,
    validate_schema_tables,
    validate_schema_columns
)


class TestClarifySQL(unittest.TestCase):

    # ============================================================
    # USER REQUEST SAFETY TESTS
    # ============================================================

    def test_read_only_request_allowed(self):

        result = validate_user_request(
            "Show me all customers"
        )

        self.assertTrue(
            result["allowed"]
        )

    def test_delete_request_blocked(self):

        result = validate_user_request(
            "Delete all customers"
        )

        self.assertFalse(
            result["allowed"]
        )

    def test_update_request_blocked(self):

        result = validate_user_request(
            "Update customer city"
        )

        self.assertFalse(
            result["allowed"]
        )

    def test_drop_request_blocked(self):

        result = validate_user_request(
            "Drop the customers table"
        )

        self.assertFalse(
            result["allowed"]
        )

    # ============================================================
    # SQL SECURITY TESTS
    # ============================================================

    def test_select_query_safe(self):

        result = validate_sql(
            "SELECT * FROM customers"
        )

        self.assertTrue(
            result["safe"]
        )

    def test_select_with_filter_safe(self):

        result = validate_sql(
            "SELECT * FROM customers "
            "WHERE city = 'Hyderabad'"
        )

        self.assertTrue(
            result["safe"]
        )

    def test_count_query_safe(self):

        result = validate_sql(
            "SELECT COUNT(*) FROM customers"
        )

        self.assertTrue(
            result["safe"]
        )

    def test_delete_sql_blocked(self):

        result = validate_sql(
            "DELETE FROM customers"
        )

        self.assertFalse(
            result["safe"]
        )

    def test_update_sql_blocked(self):

        result = validate_sql(
            "UPDATE customers SET city = 'Delhi'"
        )

        self.assertFalse(
            result["safe"]
        )

    def test_drop_sql_blocked(self):

        result = validate_sql(
            "DROP TABLE customers"
        )

        self.assertFalse(
            result["safe"]
        )

    def test_insert_sql_blocked(self):

        result = validate_sql(
            "INSERT INTO customers "
            "(customer_name) VALUES ('Test')"
        )

        self.assertFalse(
            result["safe"]
        )

    def test_multiple_statements_blocked(self):

        result = validate_sql(
            "SELECT * FROM customers; "
            "DELETE FROM customers"
        )

        self.assertFalse(
            result["safe"]
        )

    # ============================================================
    # CLARIFICATION TESTS
    # ============================================================

    def test_best_customer_requires_clarification(self):

        result = check_clarification(
            "Who is the best customer?"
        )

        self.assertTrue(
            result["needs_clarification"]
        )

        self.assertEqual(
            result["clarification_id"],
            "customer_metric"
        )

        self.assertEqual(
            len(result["options"]),
            2
        )

    def test_best_product_requires_clarification(self):

        result = check_clarification(
            "Which is the best product?"
        )

        self.assertTrue(
            result["needs_clarification"]
        )

        self.assertEqual(
            result["clarification_id"],
            "product_metric"
        )

        self.assertEqual(
            len(result["options"]),
            2
        )

    def test_normal_question_needs_no_clarification(self):

        result = check_clarification(
            "Show me all customers"
        )

        self.assertFalse(
            result["needs_clarification"]
        )

    # ============================================================
    # CONVERSATION MANAGER TESTS
    # ============================================================

    def test_total_spending_clarification(self):

        manager = ConversationManager()

        manager.store_clarification(
            session_id="test_session_1",
            original_question="Who is the best customer?",
            clarification_id="customer_metric",
            clarification=(
                "How should 'best customer' be measured?"
            ),
            options=[
                {
                    "id": "total_spending",
                    "label": "Total spending"
                },
                {
                    "id": "order_count",
                    "label": "Number of orders"
                }
            ]
        )

        result = manager.resolve_clarification(
            "test_session_1",
            "Total spending"
        )

        self.assertTrue(
            result["resolved"]
        )

        self.assertEqual(
            result["selected_option"]["id"],
            "total_spending"
        )

        self.assertIn(
            "Who is the best customer?",
            result["question"]
        )

    def test_number_option_clarification(self):

        manager = ConversationManager()

        manager.store_clarification(
            session_id="test_session_2",
            original_question="Who is the best customer?",
            clarification_id="customer_metric",
            clarification=(
                "How should 'best customer' be measured?"
            ),
            options=[
                {
                    "id": "total_spending",
                    "label": "Total spending"
                },
                {
                    "id": "order_count",
                    "label": "Number of orders"
                }
            ]
        )

        result = manager.resolve_clarification(
            "test_session_2",
            "2"
        )

        self.assertTrue(
            result["resolved"]
        )

        self.assertEqual(
            result["selected_option"]["id"],
            "order_count"
        )

    def test_invalid_clarification_answer(self):

        manager = ConversationManager()

        manager.store_clarification(
            session_id="test_session_3",
            original_question="Who is the best customer?",
            clarification_id="customer_metric",
            clarification=(
                "How should 'best customer' be measured?"
            ),
            options=[
                {
                    "id": "total_spending",
                    "label": "Total spending"
                },
                {
                    "id": "order_count",
                    "label": "Number of orders"
                }
            ]
        )

        result = manager.resolve_clarification(
            "test_session_3",
            "Blue"
        )

        self.assertFalse(
            result["resolved"]
        )

        self.assertEqual(
            len(result["options"]),
            2
        )

    def test_pending_clarification_state(self):

        manager = ConversationManager()

        self.assertFalse(
            manager.has_pending_clarification(
                "test_session_4"
            )
        )

        manager.store_clarification(
            session_id="test_session_4",
            original_question="Who is the best customer?",
            clarification_id="customer_metric",
            clarification=(
                "How should 'best customer' be measured?"
            ),
            options=[
                {
                    "id": "total_spending",
                    "label": "Total spending"
                },
                {
                    "id": "order_count",
                    "label": "Number of orders"
                }
            ]
        )

        self.assertTrue(
            manager.has_pending_clarification(
                "test_session_4"
            )
        )

        manager.resolve_clarification(
            "test_session_4",
            "Total spending"
        )

        self.assertFalse(
            manager.has_pending_clarification(
                "test_session_4"
            )
        )

    # ============================================================
    # SCHEMA VALIDATION TESTS
    # ============================================================

    def get_test_schema(self):

        return {
            "tables": {

                "customers": {
                    "columns": [
                        {
                            "column": "customer_id",
                            "type": "int"
                        },
                        {
                            "column": "customer_name",
                            "type": "varchar"
                        },
                        {
                            "column": "city",
                            "type": "varchar"
                        }
                    ],
                    "primary_keys": [
                        "customer_id"
                    ]
                },

                "orders": {
                    "columns": [
                        {
                            "column": "order_id",
                            "type": "int"
                        },
                        {
                            "column": "customer_id",
                            "type": "int"
                        },
                        {
                            "column": "total_amount",
                            "type": "decimal"
                        }
                    ],
                    "primary_keys": [
                        "order_id"
                    ]
                }
            },

            "relationships": []
        }

    def test_valid_table_reference(self):

        schema = self.get_test_schema()

        result = validate_schema_tables(
            "SELECT * FROM customers",
            schema
        )

        self.assertTrue(
            result["valid"]
        )

    def test_invalid_table_reference(self):

        schema = self.get_test_schema()

        result = validate_schema_tables(
            "SELECT * FROM employees",
            schema
        )

        self.assertFalse(
            result["valid"]
        )

    def test_valid_qualified_column(self):

        schema = self.get_test_schema()

        result = validate_schema_columns(
            "SELECT c.customer_name "
            "FROM customers c",
            schema
        )

        self.assertTrue(
            result["valid"]
        )

    def test_invalid_qualified_column(self):

        schema = self.get_test_schema()

        result = validate_schema_columns(
            "SELECT c.salary "
            "FROM customers c",
            schema
        )

        self.assertFalse(
            result["valid"]
        )


if __name__ == "__main__":

    unittest.main()