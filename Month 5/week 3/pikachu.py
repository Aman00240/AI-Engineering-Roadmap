import requests

response = requests.get('https://pokeapi.co/api/v2/pokemon/pikachu')

if response.status_code == 200:
    data = response.json()
    height = data['height']
    weight = data['weight']
    with open('pikachu.txt', 'w') as f:
        f.write(f'Height: {height}\nWeight: {weight}')
else:
    print('Failed to retrieve data')