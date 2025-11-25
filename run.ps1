# Activar el entorno virtual y ejecutar uvicorn
& .\venv\Scripts\Activate.ps1
Write-Host "Entorno virtual iniciado correctamente" -ForegroundColor Green
uvicorn main:app --reload