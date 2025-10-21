import requests
import csv

URL = "http://127.0.0.1:8080/api/v1/users/"
filepath = "src/Scripts/CSVs/users.csv"
token: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzYwOTAwNTAzLCJpYXQiOjE3NjA4MTQxMDMsInN1YiI6IjEifQ.WsvYh7Mvc3yPwXHObl56vjdmDqGpWuRHnx6QWkE-_F4"

def post_users_from_csv(csv_filepath, url, token):
    with open(csv_filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            obj = {
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "enrollment": row["enrollment"],
                "email": row["email"],
                "password": row["password"]
            }

            response = requests.post(
                url,
                data=obj,
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 201:
                print(f"User {obj['first_name']} created successfully.")
            else:
                print(f"Failed to create user {obj['first_name']}. Status code: {response.status_code}, Response: {response.text}")

    print("All users created successfully.")

if __name__ == "__main__":
    post_users_from_csv(filepath, URL, token=token)