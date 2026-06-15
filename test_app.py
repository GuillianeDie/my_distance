import pytest
from app import app, distances_history

@pytest.fixture
def client():
    """Configure le client de test Flask et réinitialise l'historique."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        distances_history.clear()  # Nettoie l'historique avant chaque test
        yield client

# ==========================================
# TESTS DE L'INTERFACE HTML (ROUTE '/')
# ==========================================

def test_html_get(client):
    """Teste l'affichage initial de la page HTML."""
    response = client.get('/')
    assert response.status_code == 200

def test_html_post_success(client):
    """Teste un calcul de distance réussi via le formulaire HTML."""
    response = client.post('/', data={'bpoint': '0,0', 'apoint': '3,4'})
    assert response.status_code == 200
    assert b"5.0" in response.data  # Pythagore: sqrt(3^2 + 4^2) = 5.0
    assert len(distances_history) == 1

def test_html_post_invalid_format(client):
    """Teste la sécurité du formulaire face à une saisie de texte invalide."""
    response = client.post('/', data={'bpoint': 'invalide', 'apoint': '3,4'})
    assert response.status_code == 400
    assert b"Format de coordonn" in response.data


# ==========================================
# TESTS DE L'API REST
# ==========================================

def test_api_get_history_empty(client):
    """Teste la récupération d'un historique vide."""
    response = client.get('/api/distances')
    assert response.status_code == 200
    assert response.json == []

def test_api_post_distance_success_list(client):
    """Teste le calcul API avec des coordonnées au format liste [x, y]."""
    response = client.post('/api/distance', json={
        'start_point': [0, 0],
        'end_point': [6, 8]
    })
    assert response.status_code == 200
    assert response.json['result_distance'] == 10.0  # sqrt(6^2 + 8^2) = 10.0

def test_api_post_distance_success_string(client):
    """Teste le calcul API avec des coordonnées au format chaîne 'x,y'."""
    response = client.post('/api/distance', json={
        'start_point': '1,1',
        'end_point': '4,5'
    })
    assert response.status_code == 200
    assert response.json['result_distance'] == 5.0

def test_api_post_distance_missing_payload(client):
    """Teste l'API lorsqu'un paramètre obligatoire est manquant."""
    response = client.post('/api/distance', json={
        'start_point': [0, 0]
    })
    assert response.status_code == 400
    assert 'error' in response.json

def test_api_post_distance_invalid_values(client):
    """Teste la robustesse de l'API face à des valeurs de coordonnées incorrectes."""
    response = client.post('/api/distance', json={
        'start_point': '0,0',
        'end_point': 'lettres,fausses'
    })
    assert response.status_code == 400
    assert 'error' in response.json