from __future__ import annotations

import csv
import json
import os
from typing import List, Dict, Optional, Any


def _to_number(val: Any) -> float:
    try:
        return float(val)
    except Exception:
        return 0.0


def generate_global_report(books: List[Dict[str, Any]], value_key: str = "value_cop", descending: bool = True) -> List[Dict[str, Any]]:
    """Genera y retorna una lista de libros ordenada por `value_key`.

    Args:
        books: lista de diccionarios que representan libros.
        value_key: campo que contiene el valor en COP.
        descending: True para mayor->menor, False para menor->mayor.

    Returns:
        Lista ordenada de diccionarios (no se muta la lista original).
    """
    if books is None:
        return []

    # Copiar y asegurar que el valor sea numérico para el ordenamiento
    def _value(b: Dict[str, Any]) -> float:
        return _to_number(b.get(value_key, 0))

    sorted_books = sorted(books, key=_value, reverse=descending)
    return sorted_books


def _collect_fieldnames(report: List[Dict[str, Any]]) -> List[str]:
    # Mantiene el orden encontrado: primero las claves del primer elemento, luego las nuevas
    seen = []
    for row in report:
        for k in row.keys():
            if k not in seen:
                seen.append(k)
    return seen


def save_report_csv(report: List[Dict[str, Any]], file_path: str, value_key: str = "value_cop") -> None:
    """Guarda el reporte en formato CSV y agrega una fila final con el total del valor.

    Args:
        report: lista de diccionarios ordenados.
        file_path: ruta donde se escribirá el CSV.
        value_key: nombre de la columna donde está el valor para sumarizar.
    """
    if report is None:
        report = []

    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

    fieldnames = _collect_fieldnames(report)
    # Si no hay una columna de valor en los datos, añadirla al final
    if value_key not in fieldnames:
        fieldnames.append(value_key)

    total = 0.0
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in report:
            # Asegurar que el writer reciba todas las keys
            safe_row = {k: (row.get(k, "") if row.get(k, None) is not None else "") for k in fieldnames}
            writer.writerow(safe_row)
            total += _to_number(row.get(value_key, 0))

        # Escribir una fila de total. La colocamos en la primera columna como 'TOTAL'.
        total_row = {k: "" for k in fieldnames}
        if len(fieldnames) > 0:
            total_row[fieldnames[0]] = "TOTAL"
        total_row[value_key] = f"{total:.2f}"
        writer.writerow({k: total_row.get(k, "") for k in fieldnames})


def save_report_json(report: List[Dict[str, Any]], file_path: str) -> None:
    """Guarda el reporte en formato JSON (lista de objetos)."""
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def generate_and_save(
    books: List[Dict[str, Any]],
    file_path: Optional[str] = None,
    format: str = "csv",
    value_key: str = "value_cop",
    descending: bool = True,
) -> List[Dict[str, Any]]:
    """Genera el reporte global y opcionalmente lo guarda en `file_path`.

    Args:
        books: lista de diccionarios con datos de libros.
        file_path: si se provee, ruta donde guardar el reporte.
        format: 'csv' o 'json'.
        value_key: clave de valor en los diccionarios.
        descending: orden descendente por valor si True.

    Returns:
        El reporte generado (lista ordenada).
    """
    report = generate_global_report(books, value_key=value_key, descending=descending)

    if file_path:
        fmt = (format or "csv").lower()
        if fmt == "csv":
            save_report_csv(report, file_path, value_key=value_key)
        elif fmt == "json":
            save_report_json(report, file_path)
        else:
            raise ValueError(f"Formato no soportado: {format}. Use 'csv' o 'json'.")

    return report


__all__ = [
    "generate_global_report",
    "save_report_csv",
    "save_report_json",
    "generate_and_save",
]