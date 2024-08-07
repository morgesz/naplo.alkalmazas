import unittest
from app import app, db, NaploBejegyzes

class NaploAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Adatbázis inicializálása
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Adatbázis törlése
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_fooldal_elerhetoseg(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_uj_bejegyzes_hozzaadasa(self):
        # Első GET kérés az új bejegyzés oldal eléréséhez, hogy megkapjuk a CSRF tokent
        response = self.app.get('/new')
        self.assertEqual(response.status_code, 200)
        
        # Kinyerjük a CSRF tokent a válaszból
        csrf_token = self._get_csrf_token(response.data.decode('utf-8'))

        # POST kérés az új bejegyzés hozzáadásához
        response = self.app.post('/new', data=dict(
            csrf_token=csrf_token,
            datum='2024-08-07',
            cim='Teszt Bejegyzés',
            tartalom='Ez egy teszt bejegyzés.'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Bejegyzés hozzáadva!', response.get_data(as_text=True))

    def _get_csrf_token(self, html):
        # Kinyerjük a CSRF tokent az űrlapból
        start = html.find('name="csrf_token" value="') + len('name="csrf_token" value="')
        end = html.find('"', start)
        return html[start:end]

if __name__ == '__main__':
    unittest.main()
