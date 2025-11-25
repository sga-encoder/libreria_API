# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
& .\venv\Scripts\Activate.ps1

# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt

Write-Host "Entorno virtual creado e instalado correctamente" -ForegroundColor Green