from flask_testing import TestCase
from source import anicondiva_init
import os

class AniconDivaTestCase(TestCase):
    def create_app(self):
        app = anicondiva_init()
        app.config['DEBUG'] = True
        return app

    def setUp(self):
        # Set up any necessary test data or state

        pass

    def tearDown(self):
        # Clean up after tests
        pass
