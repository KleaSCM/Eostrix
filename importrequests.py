import requests

api_key = 'AIzaSyAp7SmJS5G5eAz837ar2K_w91pb6JLRMPA'  # Replace with your actual API key
query = 'harry potter'  # Example query
url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'

response = requests.get(url)
if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.text)  # Print the response text for more details
#tgr
#serg
#lhrfb