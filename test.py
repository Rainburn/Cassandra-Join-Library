import time
from tabulate import tabulate
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from cassandra.metadata import TableMetadata, ColumnMetadata

from utils import *
from hash_join import *
from nested_join import *

from file_utils import *

cluster = Cluster()

# Keyspace, Table and Join Column Information
keyspace_name = 'ecommerce'
table1 = "user"
alias1 = "A"

table2 = "payment_received"
join_column = "email"
alias2 = "B"

table3 = "user_item_like"
third_join_column = "userid"
alias3 = "C"

tableInfo1_L = TableInfo(table1, join_column)
tableInfo1_R = TableInfo(table2, join_column)

tableInfo2_L = TableInfo(table1, third_join_column)
tableInfo2_R = TableInfo(table3, third_join_column)


session = cluster.connect(keyspace_name)

# Set the row factory as dictionary factory, ResultSet is List of Dictionary
session.row_factory = dict_factory

# Checking Existence of join column


# Dictionary save key-value with
# Key is the join column
# Value is the IDs from left and right table


start_time = time.time()
# -------------------------- Start here --------------------------

HashJoinExecutor(session, keyspace_name) \
    .fullOuterJoin(tableInfo1_L, tableInfo1_R) \
    .fullOuterJoin(tableInfo2_L, tableInfo2_R) \
    .execute() \
    .save_result("joinhash1")

printJoinResult("joinhash1")

# join_result = HashJoinExecutor(session, keyspace_name) \
#     .fullOuterJoin(table1, join_column, "=", table2, join_column) \
#     .rightJoin(table1, third_join_column, "=", table3) \
#     .execute()

# join_result = HashJoinExecutor(session, keyspace_name, left_table) \
#     .join(right_table, join_column) \
#     .join(third_table, third_join_column) \
#     .execute()


# join_result = NestedJoinExecutor(session, keyspace_name) \
#     .rightJoin(table1, join_column, "=", table2, join_column) \
#     .leftJoin(table1, third_join_column, "=", table3) \
#     .execute()

# join_result = NestedJoinExecutor(session, keyspace_name) \
#     .fullOuterJoin(table1, join_column, "=", table2, join_column) \
#     .execute()


print("\n\n")
# For tuple Join
# join_result = printableTupleKeyDecoder(join_result)

# For hash join
# join_result = printableHashJoinDecoder(join_result)

# print_result_as_table(join_result)

print("\n\n")


# -------------------------- End here -------------------------- 
end_time = time.time()
print()
print(f"Execution Time : {end_time - start_time} s\n")