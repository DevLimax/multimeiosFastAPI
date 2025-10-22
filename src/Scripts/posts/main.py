import asyncio
from time import sleep


from Scripts.posts.post_users import post_users_from_csv
from Scripts.posts.post_genres import post_genres_from_csv
from Scripts.posts.post_books import post_books_from_csv
from Scripts.posts.post_requests import post_requests_from_csv
from Scripts.posts.post_reviews import post_reviews_from_csv

url_base = "http://127.0.0.1:8080/api/v1/"

async def main():
    print("Iniciando o script")
    try:
        post_users_from_csv(
            csv_filepath="src/Scripts/CSVs/users.csv",
            url=url_base + "users/",
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzYxMTY0NTU4LCJpYXQiOjE3NjEwNzgxNTgsInN1YiI6IjEifQ.tXbv5R-bHulwxXGd1uNJ9g-NB5fG7ZwYQPEIihTiFvs"
        )
        sleep(5)
        post_genres_from_csv(
            csv_filepath="src/Scripts/CSVs/genres.csv",
            url=url_base + "genres/",
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzYxMTY0NTU4LCJpYXQiOjE3NjEwNzgxNTgsInN1YiI6IjEifQ.tXbv5R-bHulwxXGd1uNJ9g-NB5fG7ZwYQPEIihTiFvs"
        )
        sleep(5)
        post_books_from_csv(
            csv_filepath="src/Scripts/CSVs/books.csv",
            url=url_base + "books/",
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzYxMTY0NTU4LCJpYXQiOjE3NjEwNzgxNTgsInN1YiI6IjEifQ.tXbv5R-bHulwxXGd1uNJ9g-NB5fG7ZwYQPEIihTiFvs"
        )
        sleep(5)
        await post_requests_from_csv(
            filepath="src/Scripts/CSVs/requests.csv"
        )
        sleep(5)
        await post_reviews_from_csv(
            csv_filepath="src/Scripts/CSVs/reviews.csv"
        )
        
    except Exception as e:
        print("Erro ao executar o Script Main: ", e)
        return
    
    finally:
        print("Finalizado o Script!")
    

asyncio.run(main())