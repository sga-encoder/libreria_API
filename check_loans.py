import requests

resp = requests.get('http://localhost:8000/api/v1/loan/')
loans = resp.json().get('data', [])
print(f'\nPréstamos activos totales: {len(loans)}\n')
for loan in loans:
    print(f"- {loan['user']['fullName']}: {loan['book']['title']} (ISBN: {loan['book']['id_IBSN']})")
    print(f"  Loan ID: {loan['id']}\n")
