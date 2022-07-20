import os
import shutil
import json

from pympler import asizeof
from tabulate import tabulate

from file_utils import *


# K is the biggest prime in the first million
global K
K = 15485863

# Utils for Python Join

def print_result_as_table(result):
    # Print using Tabulate Library

    if (result == None):
        print("EMPTY RESULT SET")
        return

    if (result == []):
        print("EMPTY RESULT SET")
        return

    cols = {}
    for key in result[0]:
        cols[key] = key

    table = tabulate(result, headers=cols, tablefmt='orgtbl')

    print(table)

    return 


def partition_hash_function(M): # H1(X) Function
    # Summing all characters of the input in ASCII Number multiplied by the position of the character in the string 
    # divide the sum with big prime number P, then retrieve the remainder

    # M is input and force convert M to string
    M = str(M)

    total_sum = 0

    for i in range(len(M)):
        c = M[i]
        total_sum += ord(c) * (i+1)

    hash_value = total_sum % K

    return hash_value


def read_from_partition(join_order, partition_id, is_build):
    cwd = os.getcwd()
    tmp_folder = "tmpfolder"

    tmp_folder_path = os.path.join(cwd, tmp_folder)

    if (not os.path.isdir(tmp_folder_path)):
        print("No TmpFolder detected!")
    
    iter_path = os.path.join(tmp_folder_path, str(join_order))

    partition_path = None
    partition_name = None
    if (is_build):
        partition_name = str(partition_id) + "_l.txt"
        partition_path = os.path.join(iter_path, partition_name)

    else : # Right table
        partition_name = str(partition_id) + "_r.txt"
        partition_path = os.path.join(iter_path, partition_name)

    # File not found check
    if (not os.path.isfile(partition_path)):
        print(f"Partition {partition_name} from Join Order : {join_order} is not found!")
        return None

    f = open(partition_path, 'r')
    data = f.readlines()

    print("READ FROM PARTITION RESULT : ", data)

    return data


def read_from_partition_nonhash(join_order, partition_id, is_left_table):
    cwd = os.getcwd()
    tmp_folder = "tmpfolder"

    tmp_folder_path = os.path.join(cwd, tmp_folder)

    if (not os.path.isdir(tmp_folder_path)):
        print("No TmpFolder detected!")
    
    iter_path = os.path.join(tmp_folder_path, str(join_order))

    partition_path = None
    partition_name = None
    if (is_left_table):
        partition_name = str(partition_id) + "_l.txt"
        partition_path = os.path.join(iter_path, partition_name)

    else : # Right table
        partition_name = str(partition_id) + "_r.txt"
        partition_path = os.path.join(iter_path, partition_name)

    # File not found check
    if (not os.path.isfile(partition_path)):
        print(f"Partition {partition_name} from Join Order : {join_order} is not found!")
        return None

    f = open(partition_path, 'r')
    data = f.readlines()

    # Reformat data
    for idx in range(len(data)):
        curr_data = data[idx]
        print(curr_data[:-1])
        data[idx] = json.loads(curr_data[:-1])

    data = jsonTupleKeyDecoder(data)

    return data


def put_into_partition(data_page, join_order, join_column, is_left_table):

    hash_values_set = set()

    cwd = os.getcwd()
    tmp_folder_name = "tmpfolder"

    tmp_folder_path = os.path.join(cwd, tmp_folder_name)

    if (not os.path.isdir(tmp_folder_path)):
        os.mkdir(tmp_folder_path)

    iter_path = os.path.join(tmp_folder_path, str(join_order))

    if (not os.path.isdir(iter_path)):
        os.mkdir(iter_path)

    for data in data_page:
        join_column_value = data[join_column]
        partition_number = partition_hash_function(join_column_value)

        partition_filename = None

        if (is_left_table):
            partition_filename = str(partition_number) + "_l" + ".txt"
        else :
            partition_filename = str(partition_number) + "_r" + ".txt"
            
        parittion_fullname = os.path.join(iter_path, partition_filename)

        hash_values_set.add(partition_number)

        f = open(parittion_fullname, mode='a')
        f.write(json.dumps(data)+"\n")
        f.close()
    

    # After use all temps, delete tmpfolder
    # shutil.rmtree(tmp_folder_path)

    return hash_values_set


def put_into_partition_nonhash(data_page, join_order, max_partition_size, last_partition_id, is_left_table):
    partition_data = []

    last_partition_size = 0

    cwd = os.getcwd()
    tmp_folder_name = "tmpfolder"

    tmp_folder_path = os.path.join(cwd, tmp_folder_name)

    if (not os.path.isdir(tmp_folder_path)):
        os.mkdir(tmp_folder_path)

    iter_path = os.path.join(tmp_folder_path, str(join_order))

    if (not os.path.isdir(iter_path)):
        os.mkdir(iter_path)

    if (last_partition_id != -1):
        last_partition_name = str(last_partition_id)
        if (is_left_table):
            last_partition_name += "_l.txt"

        else :
            last_partition_name += "_r.txt"

        # Check size of last partition
        last_partition_path = os.path.join(iter_path, last_partition_name)
        last_partition_size = os.path.getsize(last_partition_path)


    # Make partition
    for data_idx in range(len(data_page)):
        row = data_page[data_idx]
        partition_data.append(row)
        
        # Clear row to maintain memoru usage
        data_page[data_idx] = None

        # TODO: THE PROBLEM IS HERE. MAX PARTITION SIZE IS TOO BIG FOR SMALL TEST CASE
        if (asizeof.asizeof(partition_data) + last_partition_size >= max_partition_size):
            # Flush into partition
            new_last_partition_id = last_partition_id + 1
            new_last_partition_name = str(new_last_partition_id)

            if (is_left_table):
                new_last_partition_name += "_l.txt"
            
            else :
                new_last_partition_name += "_r.txt"

            new_last_partition_path = os.path.join(iter_path, new_last_partition_name)

            # Convert data to json accepted format
            partition_data = jsonTupleKeyEncoder(partition_data)

            # File operation
            f = open(new_last_partition_path, mode='a')

            # Write data here
            for row in partition_data:
                f.write(json.dumps(row)+"\n")

            f.close()

            # Empty the partition data
            partition_data = []

            # Increment last partition id and reset partition size
            last_partition_id = new_last_partition_id
            if (last_partition_size != 0):
                last_partition_size = 0

        
    # Force flush partition
    new_last_partition_id = last_partition_id + 1
    new_last_partition_name = str(new_last_partition_id)

    if (is_left_table):
        new_last_partition_name += "_l.txt"

    else :
        new_last_partition_name += "_r.txt"

    new_last_partition_path = os.path.join(iter_path, new_last_partition_name)

    # Convert data to json accepted format
    partition_data = jsonTupleKeyEncoder(partition_data)

    f = open(new_last_partition_path, mode='a')
    # Write data here
    for row in partition_data:
        f.write(json.dumps(row)+"\n")
    f.close()

    partition_data = []
    
    # Increment last partition id
    last_partition_id = new_last_partition_id

    return last_partition_id


def update_partition_nonhash(partition_data, join_order, partition_id, is_left_table):

    cwd = os.getcwd()

    tmp_folder_name = "tmpfolder"
    tmp_folder_path = os.path.join(cwd, tmp_folder_name)

    iter_path = os.path.join(tmp_folder_path, str(join_order))

    partition_name = str(partition_id)

    if (is_left_table):
        partition_name += "_l.txt"

    else:
        partition_name += "_r.txt"

    partition_path = os.path.join(iter_path, partition_name)

    if (not os.path.exists(partition_path)):
        if (is_left_table):
            print(f"Left Partition {partition_id} on Join order {join_order} cannot be found!")
        else:
            print(f"Right Partition {partition_id} on Join order {join_order} cannot be found!")
        
        return False


    # Convert data
    partition_data = jsonTupleKeyEncoder(partition_data)

    # Open partition and update (re-write) partition
    f = open(partition_path, mode='w')

    for row in partition_data:
        f.write(json.dumps(row)+"\n")
    f.close()

    return True


def empty_table_guard(dataset):

    if (dataset == None):
        return True

    return False

def get_column_names_from_db(session, keyspace, table):
    # Get column names for Cassandra 3.x and above
    cql = f"SELECT column_name from system_schema.columns WHERE keyspace_name = '{keyspace}' AND table_name = '{table}';"

    result_set = session.execute(cql)
    column_names = set()

    for column in result_set:
        column_name = column['column_name']
        column_names.add(column_name)

    return column_names

def get_column_names_from_local(join_order, partition_ids):
    # Assume this method only required for left-table
    column_names = set()
    partition_ids = list(partition_ids)

    first_id = partition_ids[0]

    cwd = os.getcwd()
    tmp_folder = "tmpfolder"

    tmp_folder_path = os.path.join(cwd, tmp_folder)

    if (not os.path.isdir(tmp_folder_path)):
        print("No TmpFolder detected!")
    
    iter_path = os.path.join(tmp_folder_path, str(join_order))
    first_id_path = os.path.join(iter_path, str(first_id) + "_l.txt")

    # Read from file
    f = open(first_id_path, 'r')
    first_data = f.readline()
    convert_to_dict = json.loads(first_data[:-1])

    for key in convert_to_dict:
        column_names.add(key)

    return column_names


def construct_null_columns(table_name, column_names):

    null_columns = {}
    for col_name in column_names:
        key = (col_name, table_name)
        null_columns[key] = None

    return null_columns