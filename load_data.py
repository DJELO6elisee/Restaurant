import json
import mysql.connector
from datetime import datetime

# Configuration of your MySQL database
db_config = {
    "host": "127.0.0.1",  # usually "localhost"
    "user": "root",
    "password": "",
    "database": "django_db",
}


def load_json_to_mysql(file_path, table_mapping):
    """Loads data from a JSON file into multiple MySQL tables based on a mapping."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file '{file_path}'")
        return

    try:
        # Connect to the MySQL database
        mydb = mysql.connector.connect(**db_config)
        cursor = mydb.cursor()

        # Check if data is a list
        if not isinstance(data, list):
            print("Error: Expected JSON data to be a list (JSON array).")
            mydb.close()
            return

        for item in data:
            # Check if the item is a dict (object)
            if isinstance(item, dict):
                # Apply mapping based on some key or condition (e.g., type of data)
                table_name = map_item_to_table(item, table_mapping)
                if table_name:
                    try:
                       column_names = ", ".join(item.keys())
                       placeholders = ", ".join(["%s"] * len(item))
                       sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
                       val = tuple(item.values())
                       # handle datetime conversion for date columns
                       val_list = []
                       for value in val:
                         if isinstance(value, str):
                           try:
                             date_object = datetime.fromisoformat(value)
                             val_list.append(date_object)
                           except ValueError:
                             val_list.append(value) # leave it as string if not datetime
                         else:
                           val_list.append(value)
                       val = tuple(val_list)
                       cursor.execute(sql, val)
                    except Exception as e:
                       print(f"Error inserting into table {table_name}: {e}")

                else:
                    print(f"Warning: No table mapping found for item {item}. Skipping.")
            # Handle array of strings as before
            elif isinstance(item, str):
                table_name = table_mapping.get("default_table")
                if table_name:
                    sql = "INSERT INTO {} (name) VALUES (%s)".format(table_name)
                    val = (item,)
                    cursor.execute(sql, val)
                else:
                    print(f"Warning: No default table mapping found for item {item}. Skipping.")
            else:
                 print(f"Warning: Unknown data type for item {item}. Skipping.")


        mydb.commit()
        print(f"Data from '{file_path}' has been loaded successfully.")
    except mysql.connector.Error as err:
        print(f"Error interacting with MySQL: {err}")
    finally:
        if mydb.is_connected():
            cursor.close()
            mydb.close()


def map_item_to_table(item, table_mapping):
    """Maps an item from the JSON data to a table based on the mapping"""
    if "type" in item:
       data_type = item.get("type")
       if data_type in table_mapping:
           return table_mapping[data_type]
    return None

if __name__ == "__main__":
    json_file_path = "data.json"  # Path to your data.json file

    # Define table mapping - customize the dict!
    table_mapping = {
        "regimealimentaire": "shop_regimealimentaire",
        "category": "shop_category",
        "product": "shop_product",
        "commande": "shop_commande",
        "detailcommande": "shop_detailcommande",
        "message": "shop_message",
        "order": "shop_order",
        "profileutilisateur": "shop_profileutilisateur",
        "customuser": "connexion_customuser",
        "default_table": "names"
    }
    load_json_to_mysql(json_file_path, table_mapping)