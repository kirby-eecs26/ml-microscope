import unittest
from backend.save import *
from unittest.mock import patch
from io import StringIO

class TestSave(unittest.TestCase):

    def setUp(self):
        capture_id = "N/A"

