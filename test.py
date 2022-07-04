import time
from tabulate import tabulate
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from cassandra.metadata import TableMetadata, ColumnMetadata

from utils import *
from join import *

cluster = Cluster()

# Keyspace, Table and Join Column Information
keyspace_name = 'ecommerce'
left_table = "user"
right_table = "payment_received"
join_column = "email"

third_table = "user_item_like"
third_join_column = "userid"

session = cluster.connect(keyspace_name)

# Set the row factory as dictionary factory, ResultSet is List of Dictionary
session.row_factory = dict_factory

# Checking Existence of join column


intermediate_result = IntermediateResult(join_column)
# Dictionary save key-value with
# Key is the join column
# Value is the IDs from left and right table


start_time = time.time()
# -------------------------- Start here --------------------------


join_result = JoinExecutor(session, keyspace_name, left_table) \
    .join(right_table, join_column) \
    .join(third_table, third_join_column) \
    .execute()

print("\n\n")
print_result_as_table(join_result)
print("\n\n")


# -------------------------- End here -------------------------- 
end_time = time.time()
print()
print(f"Execution Time : {end_time - start_time} s\n")