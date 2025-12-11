import requests

resp = requests.get('http://localhost:8000/api/v1/book/')
books = resp.json()['data']
print(f'\nTotal libros en inventario: {len(books)}\n')

for i, b in enumerate(books, 1):
    print(f'{i:2d}. {b["title"]:40s} - {b["weight"]} kg - Prestado: {b.get("is_borrowed", False)}')

print(f'\nTotal: {len(books)} libros')
print(f'Prestados: {sum(1 for b in books if b.get("is_borrowed", False))}')
print(f'Disponibles: {sum(1 for b in books if not b.get("is_borrowed", False))}')
