import csv
import re
from collections import Counter
from itertools import combinations


def extract_slug(url):
    """
    Extrae el slug de una URL eliminando el dominio y los parámetros.
    """
    return re.sub(r"https?:\/\/[^\/]+\/?", "", url).split("?")[0]


def alphanumeric_match_count(slug_a, slug_b):
    """
    Calcula el número de coincidencias alfanuméricas entre dos slugs.
    """
    return sum((Counter(re.findall(r"\w+", slug_a)) & Counter(re.findall(r"\w+", slug_b))).values())


def find_best_matches(url_list_a, url_list_b, min_match=4):
    """
    Encuentra los mejores emparejamientos de URLs entre dos listas basado en coincidencias alfanuméricas.
    """
    results = []
    
    for url_a in url_list_a:
        slug_a = extract_slug(url_a)
        matches = []
        
        for url_b in url_list_b:
            slug_b = extract_slug(url_b)
            match_count = alphanumeric_match_count(slug_a, slug_b)
            
            if match_count >= min_match:
                matches.append((url_b, match_count))
        
        # Ordenar coincidencias para la URL actual de mayor a menor
        matches = sorted(matches, key=lambda x: x[1], reverse=True)
        
        # Si hay al menos dos coincidencias, guardarlas en los resultados
        if len(matches) > 0:
            best_match = matches[0]
            second_best_match = matches[1] if len(matches) > 1 else ("", 0)
            results.append((url_a, best_match[0], best_match[1], second_best_match[0], second_best_match[1]))
    
    # Ordenar todos los resultados de mayor a menor coincidencia
    results = sorted(results, key=lambda x: x[2], reverse=True)
    return results


def save_to_csv(results, output_file):
    """
    Guarda los resultados en un archivo CSV.
    """
    headers = ["Elemento A", "Elemento B", "Coincidencia", "Elemento B2", "Coincidencia B2"]
    
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(results)


if __name__ == "__main__":
    # Ejemplo de listas de URLs
    url_list_a = [
        "https://example.com/slug-1",
        "https://example.com/slug-2",
        "https://example.com/slug-3"
    ]
    
    url_list_b = [
        "https://example.com/matching-slug-1",
        "https://example.com/slug-2-extra",
        "https://example.com/another-slug"
    ]
    
    # Encontrar emparejamientos
    results = find_best_matches(url_list_a, url_list_b, min_match=4)
    
    # Guardar en un archivo CSV
    save_to_csv(results, "output.csv")
    print(f"Resultados guardados en output.csv")
