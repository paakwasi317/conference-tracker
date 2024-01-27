import unittest
from io import BytesIO
from utils.scheduler import Scheduler, SchedulingError, TalkInfo

class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = Scheduler()

    def test_valid_csv(self):
        '''Test case for clean_data method with valid CSV'''
        
        valid_csv_data = b"Talk 1 45 mins\nTalk 2 lightning\n"
        file_byte_valid = BytesIO(valid_csv_data)
        self.scheduler.clean_data(file_byte_valid)
        print(self.scheduler.conference_data)
        self.assertEqual(len(self.scheduler.conference_data), 2)
        self.assertEqual(self.scheduler.conference_data[0], TalkInfo(conference_talk='Talk 1', duration=45))
        self.assertEqual(self.scheduler.conference_data[1], TalkInfo(conference_talk='Talk 2 lightning', duration=5))

    def test_with_invalid_csv(self):
        '''Test case for clean_data method with invalid CSV(comma introduced makes it invalid). 
           Always stringify to escape comma'''
        
        invalid_csv_data = b"Talk 1, 45 mins\nTalk 2 lightning\n"
        file_byte_invalid = BytesIO(invalid_csv_data)
        self.assertRaises(Exception, lambda: self.scheduler.clean_data(file_byte_invalid))

    def test_with_empty_csv(self):
        '''Test case for empty csv'''
        
        empty_csv_data = b""
        file_byte_invalid = BytesIO(empty_csv_data)
        self.assertRaises(SchedulingError, lambda: self.scheduler.clean_data(file_byte_invalid))

    def test_create_multiple_tracks(self):
        '''Test case for multiple tracks'''

        self.scheduler.conference_data = {
            "1": TalkInfo(conference_talk="Talk 1", duration=60),
            "2": TalkInfo(conference_talk="Talk 2", duration=45),
            "3": TalkInfo(conference_talk="Talk 3", duration=30),
            "4": TalkInfo(conference_talk="Talk 4", duration=60),
            "5": TalkInfo(conference_talk="Talk 5", duration=45),
            "6": TalkInfo(conference_talk="Talk 6", duration=30),
            "7": TalkInfo(conference_talk="Talk 7", duration=90),
            "8": TalkInfo(conference_talk="Talk 8", duration=60),
            "9": TalkInfo(conference_talk="Talk 9", duration=40),
            "10": TalkInfo(conference_talk="Talk 10",duration=5),
        }
        result = self.scheduler.create_tracks()
        self.assertEqual(len(result), 2)
        self.assertIn("Track 1", result[0])
        self.assertIn("Track 2", result[1])

    def test_create_one_track(self):
        '''Test case to create one track'''

        self.scheduler.conference_data = {
            "1": TalkInfo(conference_talk="Talk 1", duration=45),
            "2": TalkInfo(conference_talk="Talk 2", duration=30),
            "3": TalkInfo(conference_talk="Talk 3", duration=60),
        }
        result = self.scheduler.create_tracks()
        self.assertEqual(len(result), 1)
        self.assertIn("Track 1", result[0])
        self.assertEqual(len(result[0]["Track 1"]), 5)

    def test_create_one_track_one_talk(self):
        '''Test case for create_multiple_schedules method with valid data but one talk'''

        self.scheduler.conference_data = {
            "1": TalkInfo(conference_talk="Talk 1", duration=45)
        }
        result = self.scheduler.create_tracks()
        self.assertEqual(len(result), 1)
        self.assertIn("Track 1", result[0])
        self.assertEqual(len(result[0]["Track 1"]), 3)

    def test_create_track_with_no_data(self):
        '''Test case to create track with no data'''

        self.scheduler.conference_data = {}
        result = self.scheduler.create_tracks()
        self.assertEqual(len(result), 0)

if __name__ == "__main__":
    unittest.main()
