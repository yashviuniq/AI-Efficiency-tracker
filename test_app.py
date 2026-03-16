
import unittest
import json
import app
import database

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.database.init_db()
        self.app = app.app.test_client()
        self.app.testing = True

    def test_get_stats_empty(self):
        response = self.app.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        # Should be a list (empty or not depending on DB state from previous runs)
        self.assertIsInstance(json.loads(response.data), list)

    def test_log_activity_and_goal(self):
        # Set Goal
        goal_payload = {"category": "TestCat", "hours": 10}
        response = self.app.post('/api/goal', json=goal_payload)
        self.assertEqual(response.status_code, 200)
        
        # Log Activity
        log_payload = {"activity": "Testing API", "category": "TestCat", "duration": 60}
        response = self.app.post('/api/log', json=log_payload)
        self.assertEqual(response.status_code, 200)
        
        # Verify Stats
        response = self.app.get('/api/stats')
        data = json.loads(response.data)
        
        # Find our TestCat
        found = False
        for item in data:
            if item['category'] == 'TestCat':
                found = True
                self.assertEqual(item['Actual Hours'], 1.0)
                # 1 hour / 10 hours = 10%
                self.assertEqual(item['Efficiency %'], 10.0)
                break
        self.assertTrue(found, "TestCat not found in stats")

    def test_predict_category(self):
        response = self.app.get('/api/predict_category?activity=Coding')
        data = json.loads(response.data)
        # Should return a category or null
        self.assertIn("category", data)

if __name__ == '__main__':
    unittest.main()
