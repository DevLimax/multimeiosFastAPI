import requests
import csv

URL = "http://127.0.0.1:8000/api/v1/genres/"
filepath = "src/Scripts/CSVs/genres.csv"
token: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzYwOTAwNTAzLCJpYXQiOjE3NjA4MTQxMDMsInN1YiI6IjEifQ.WsvYh7Mvc3yPwXHObl56vjdmDqGpWuRHnx6QWkE-_F4"

def post_genres_from_csv(csv_filepath: str, url: str, token: str):
    with open(csv_filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            response = requests.post(
               url,
               json=row,
                headers={"Authorization": f"Bearer {token}"}
            ) 
            if response.status_code == 201:
                print(f"Genre {row['name']} created successfully.")
            else:
                print(f"Failed to create genre {row['name']}. Status code: {response.status_code}, Response: {response.text}")

    print("All genres created successfully.")
        
if __name__ == "__main__":
    post_genres_from_csv(filepath, URL)