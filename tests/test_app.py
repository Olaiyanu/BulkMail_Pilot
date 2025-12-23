import unittest
from app import create_app, db
from app.models import Recipient

class BulkMailTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_recipient(self):
        response = self.client.post('/api/recipients', json={
            'email': 'test@example.com',
            'name': 'Test User'
        })
        self.assertEqual(response.status_code, 201)
        
        with self.app.app_context():
            r = Recipient.query.first()
            self.assertEqual(r.email, 'test@example.com')

    def test_dashboard_load(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BulkMail Pilot', response.data)

if __name__ == '__main__':
    unittest.main()
