import unittest


@unittest.skip("Auth tests are outdated and depend on external Google flow; to be rewritten to mock Flow.from_client_config and HTTP server.")
class TestOAuthHandler(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()