import requests
import csv

URL = "http://127.0.0.1:8000/api/v1/books/"
filepath = "src/Scripts/CSVs/books.csv"
token: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzYwOTAwNTAzLCJpYXQiOjE3NjA4MTQxMDMsInN1YiI6IjEifQ.WsvYh7Mvc3yPwXHObl56vjdmDqGpWuRHnx6QWkE-_F4"

def post_books_from_csv(csv_filepath: str, url: str, token: str):
    with open(csv_filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row['genre_two'].lower() == 'null' or row['genre_two'] == '':
                row.pop('genre_two')
            response = requests.post(
                url,
                data=row,
                headers={"Authorization": f"Bearer {token}"}
            ) 
            if response.status_code == 201:
                print(f"Book {row['title']} created successfully.")
            else:
                print(f"Failed to create book {row['title']}. Status code: {response.status_code}, Response: {response.text}")

    print("All books created successfully.")
    
if __name__ == "__main__":
    post_books_from_csv(filepath, URL)