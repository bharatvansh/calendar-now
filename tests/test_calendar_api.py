import unittest


@unittest.skip("Outdated tests referencing removed CalendarClient/CalendarEvent; to be rewritten against GoogleCalendarClient with mocks.")
class TestCalendarAPI(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()