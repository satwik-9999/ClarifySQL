from sql_generator import validate_sql


test_queries = [

    "SELECT * FROM customers",

    "SELECT * FROM customers WHERE city = 'Hyderabad'",

    "SELECT COUNT(*) FROM customers",

    "SELECT * FROM customers; DELETE FROM customers",

    "DELETE FROM customers",

    "UPDATE customers SET city = 'Delhi'",

    "DROP TABLE customers",

    "INSERT INTO customers (customer_name) VALUES ('Test')"

]


for sql in test_queries:

    result = validate_sql(sql)

    print("\nSQL:")
    print(sql)

    print("Result:")
    print(result)