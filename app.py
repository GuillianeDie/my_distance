from flask import Flask, request, render_template, jsonify
from math import sqrt
from datetime import datetime

app = Flask('my_distance')

# Utilisation du snake_case et renommage explicite de la variable globale
distances_history = []

def calculate_euclidean_distance(point_a, point_b):
    """Calcule la distance mathématique entre deux points 2D (Théorème de Pythagore).
    Centraliser cette formule évite la duplication de code (principe DRY).
    """
    return sqrt((point_b[0] - point_a[0])**2 + (point_b[1] - point_a[1])**2)

def parse_coordinate_string(coord_str):
    """Parse une chaîne 'x,y' en un tuple d'entiers (x, y) avec gestion d'erreur."""
    try:
        parts = coord_str.split(',')
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        raise ValueError("Format de coordonnée invalide. Format attendu : 'x,y' avec des entiers.")

@app.route('/', methods=['GET', 'POST'])
def html_calculate():
    """Gère l'interface utilisateur HTML."""
    if request.method == 'GET':
        return render_template('index.html', result=None)
    
    # Méthode POST
    try:
        start_point = parse_coordinate_string(request.form.get('bpoint', ''))
        end_point = parse_coordinate_string(request.form.get('apoint', ''))
        
        distance = calculate_euclidean_distance(start_point, end_point)
        
        result = {
            'requested_at': datetime.now(),
            'result_distance': distance,
            'start_point': start_point,
            'end_point': end_point
        }
        distances_history.append(result)
        return render_template('index.html', result=result)
    except ValueError as e:
        # Sécurisation de l'interaction utilisateur (évite les crashs 500)
        return render_template('index.html', error=str(e)), 400

@app.route('/api/distances', methods=['GET'])
def get_distances_history():
    """Endpoint REST pour récupérer l'historique (uniquement en GET)."""
    return jsonify(distances_history)

@app.route('/api/distance', methods=['POST'])
def api_calculate_distance():
    """Endpoint REST pour calculer une distance (uniquement en POST).
    Respecte la sémantique HTTP et accepte un payload JSON propre.
    """
    data = request.get_json()
    if not data or 'start_point' not in data or 'end_point' not in data:
        return jsonify({'error': 'Données manquantes (start_point ou end_point)'}), 400
    
    try:
        # Supporte le format chaîne "x,y" ou une liste [x, y] pour plus de robustesse
        if isinstance(data['start_point'], str):
            start_point = parse_coordinate_string(data['start_point'])
        else:
            start_point = (int(data['start_point'][0]), int(data['start_point'][1]))
            
        if isinstance(data['end_point'], str):
            end_point = parse_coordinate_string(data['end_point'])
        else:
            end_point = (int(data['end_point'][0]), int(data['end_point'][1]))
            
        distance = calculate_euclidean_distance(start_point, end_point)
        
        return jsonify({
            'requested_at': datetime.now().isoformat(),
            'result_distance': distance,
            'start_point': start_point,
            'end_point': end_point
        }), 200
    except (ValueError, IndexError, TypeError) as e:
        return jsonify({'error': f'Données invalides : {str(e)}'}), 400