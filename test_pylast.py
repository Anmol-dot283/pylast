#!/usr/bin/env python
"""
Integration (not unit) tests for pylast.py
"""
import datetime
import time
import unittest
import yaml # pip install pyyaml

import pylast

def load_secrets():
    with open("test_pylast.yaml", "r") as f: # see test_pylast_example.yaml
        doc = yaml.load(f)
    print doc
    print doc["username"]
    return doc

class TestSequenceFunctions(unittest.TestCase):

    secrets = None

    def unix_timestamp(self):
        return int(time.mktime(datetime.datetime.now().timetuple()))

    def setUp(self):
        if self.__class__.secrets is None:
            self.__class__.secrets = load_secrets()

        self.username = self.__class__.secrets["username"]
        password_hash = self.__class__.secrets["password_hash"]

        API_KEY       = self.__class__.secrets["api_key"]
        API_SECRET    = self.__class__.secrets["api_secret"]

        self.network = pylast.LastFMNetwork(api_key = API_KEY, api_secret =
    API_SECRET, username = self.username, password_hash = password_hash)


    def test_scrobble(self):
        # Arrange
        artist = "Test Artist"
        title = "Test Title"
        timestamp = self.unix_timestamp()
        lastfm_user = self.network.get_user(self.username)

        # Act
        self.network.scrobble(artist = artist, title = title, timestamp = timestamp)

        # Assert
        last_scrobble = lastfm_user.get_recent_tracks(limit = 1)[0]
        self.assertEqual(str(last_scrobble.track.artist), str(artist))
        self.assertEqual(str(last_scrobble.track.title),  str(title))
        self.assertEqual(str(last_scrobble.timestamp),    str(timestamp))


    def test_unscrobble(self):
        # Arrange
        artist = "Test Artist 2"
        title = "Test Title 2"
        timestamp = self.unix_timestamp()
        library = pylast.Library(user = self.username, network = self.network)
        self.network.scrobble(artist = artist, title = title, timestamp = timestamp)
        lastfm_user = self.network.get_user(self.username)

        # Act
        library.remove_scrobble(artist = artist, title = title, timestamp = timestamp)

        # Assert
        last_scrobble = lastfm_user.get_recent_tracks(limit = 1)[0]
        self.assertNotEqual(str(last_scrobble.timestamp), str(timestamp))


    def test_add_album(self):
        # Arrange
        library = pylast.Library(user = self.username, network = self.network)
        album = self.network.get_album("Test Artist", "Test Album")

        # Act
        library.add_album(album)

        # Assert
        # Nothing here, just that no exception occurred


    def test_get_venue(self):
        # Arrange
        venue_name = "Last.fm Office"
        country_name = "United Kingom"

        # Act
        venue_search = self.network.search_for_venue(venue_name, country_name)
        venue = venue_search.get_next_page()[0]

        # Assert
        self.assertEqual(str(venue.id), "8778225")


    def test_get_user_registration(self):
        # Arrange
        username = "RJ"
        user = self.network.get_user(username)

        # Act
        registered = user.get_registered()

        # Assert
        # Just check date because of timezones
        self.assertIn(u"2002-11-20 ", registered)


    def test_get_user_unixtime_registration(self):
        # Arrange
        username = "RJ"
        user = self.network.get_user(username)

        # Act
        unixtime_registered = user.get_unixtime_registered()

        # Assert
        # Just check date because of timezones
        self.assertEquals(unixtime_registered, u"1037793040")

    def test_get_genderless_user(self):
        # Arrange
        lastfm_user = self.network.get_user("test_user") # currently no gender set

        # Act
        gender = lastfm_user.get_gender()

        # Assert
        self.assertIsNone(gender)


    def test_get_countryless_user(self):
        # Arrange
        lastfm_user = self.network.get_user("test_user") # currently no country set

        # Act
        country = lastfm_user.get_country()

        # Assert
        self.assertIsNone(country)

if __name__ == '__main__':
    unittest.main()

# End of file
