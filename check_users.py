import requests

resp = requests.get('http://localhost:8000/api/v1/user/')
users = resp.json()['data']
print(f'\nTotal usuarios: {len(users)}\n')
for i, u in enumerate(users):
    print(f'{i+1}. {u["fullName"]} ({u["email"]})')
    if u.get("loans"):
        print(f'   Préstamos: {u["loans"]}')
