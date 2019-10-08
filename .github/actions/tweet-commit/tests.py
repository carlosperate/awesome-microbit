import os
import unittest

try:
    import tweet_commit
except ImportError:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    import tweet_commit


class TestCommitTweet(unittest.TestCase):
    """Tests that commits in this repo are parsed correctly.

    This tests depend on the git history from the awesome-microbit repo, not
    a great way to test this (we could mock a the git library), but a quick
    way to get this tested.
    """

    def test_commit_1(self):
        """Normal commit."""
        title, url, description = tweet_commit.get_commit_list_entry('2c58c69cd5ea09fe15726d60c40faaccc6735921')
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, 'MB1013: Module for the MB1013 ultrasonic sensor controlled via UART.\nhttps://github.com/liamkinne/microbit-mb1013')

    def test_commit_2(self):
        """Merge commit."""
        title, url, description = tweet_commit.get_commit_list_entry('401d6c4ee70d21dd86631eb377433b319cbb88d1')
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, 'ESP8266/ThingSpeak: Use a ESP8266 wifi module to upload data to ThingSpeak.com.\nhttps://github.com/alankrantas/pxt-ESP8266_ThingSpeak')

    def test_commit_3(self):
        """Normal commit with extra dots in the middle."""
        title, url, description = tweet_commit.get_commit_list_entry("2faac881c36435b45a454989ca915f50fe919c94")
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, "The Christmas Joy Spreading Machine: Project inside a box representing a metaphor of the most popular Christmas symbols. Maybe it's a bit distopyc but it moves, lights and reacts to music.\nhttps://www.hackster.io/balearicdynamics/the-christmas-joy-spreading-machine-3d3559")

    def test_commit_4(self):
        """Invalid awesome list entry."""
        with self.assertRaises(Exception) as context:
            title, url, description = tweet_commit.get_commit_list_entry('fa544e2c211eb47ac1cb287df5f5c09edabb2ae0')

        self.assertTrue('Could not match an awesome list entry.' in str(context.exception))

    def test_commit_5(self):
        """Normal commit with brackets."""
        title, url, description = tweet_commit.get_commit_list_entry("d8eaa108e6fbb635f282f341e64b7b36507f0788")
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, "Ironman Arc Reactor: Choose between two different versions (Mk I and Mk II) ready to 3D print and build.\nhttps://www.kitronik.co.uk/blog/halo-ween-ironman-arc-reactor")

    def test_commit_6(self):
        """Markdown link inside the list entry description."""
        title, url, description = tweet_commit.get_commit_list_entry('5652ef8bf0d617a3d4085429f4d39007b44ef09d')
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, 'Official Swift Playgrounds: ([Source Code](https://github.com/microbit-foundation/microbit-swift-playgrounds)) Swift Playgrounds is an app for the iPad that helps teach people to code in the Swift language using interactive \'books\'.\nhttps://microbit.org/guide/swift-playgrounds/')

    def test_commit_replace_microbit_1(self):
        """Replace microbit for #microbit in description."""
        title, url, description = tweet_commit.get_commit_list_entry("efeffb853b72a6df40cb2a0dad45c1b3384aba2f")
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, "Otto Robot: Otto chassis for the #microbit to make a bidepad robot with a robitbit accessory.\nhttps://www.thingiverse.com/thing:2786066")

    def test_commit_replace_microbit_2(self):
        """Replace micro:bit for #microbit in description, but not in title."""
        title, url, description = tweet_commit.get_commit_list_entry("5a04d4c8a4d51c10ee87a0d69656bb1c695447f1")
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, "Grade 10 micro:bit Tutorials: Collection of short videos showing how to use #microbit MakeCode blocks and features.\nhttps://www.youtube.com/playlist?list=PLo6KSCBvKXc92f7p8ONiBeWAJKIqNpKlr")


if __name__ == '__main__':
    project_root_dir = \
        os.path.dirname(os.path.dirname(os.path.dirname(    # Going up 3 levels
            os.path.dirname(os.path.realpath(__file__)))))  # This file folder dir
    os.chdir(project_root_dir)
    unittest.main()
