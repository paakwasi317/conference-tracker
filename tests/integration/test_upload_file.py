import io
import json
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from tracker.webserver import tracker_api
from utils.scheduler import Scheduler

class TestTrackerAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(tracker_api)

    def tearDown(self):
        self.client.close()

    def test_create_upload_file_valid_csv(self):
        '''Assuming you have a valid CSV content in bytes'''

        valid_csv_content = b"talks\nTalk 1 \nTalk 2 78mins"

        with patch.object(Scheduler, 'create_tracks') as mock_create_schedules:
            mock_create_schedules.return_value = [{'Track 1': [{'time': '09:00 AM', 'talk': 'Talk 1'}]}]

            response = self.client.post("/tracker/uploadfile", files={"file": ("test.csv", valid_csv_content)})

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("schedules", data)

    def test_create_upload_file_empty_csv(self):
        '''Assuming you have an empty CSV content in bytes'''

        empty_csv_content = b""
        with self.assertRaises(HTTPException) as context:
            response = self.client.post("/tracker/uploadfile", files={"file": ("empty.csv", empty_csv_content)})
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn("detail", data)
            self.assertIn("Empty CSV file", data["detail"])

    def test_create_upload_file_invalid_csv(self):
        '''Assuming you have an invalid CSV content in bytes'''

        invalid_csv_content = b"invalid,,"

        with self.assertRaises(HTTPException) as context:
            response = self.client.post("/tracker/uploadfile", files={"file": ("invalid.csv", invalid_csv_content)})
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn("detail", data)
            self.assertIn("Invalid CSV file", data["detail"])

if __name__ == "__main__":
    unittest.main()
