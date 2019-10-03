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
        title, url, description = tweet_commit.get_commit_list_entry('f219e79ff490f784d8a6bb8807149034dded68a8')
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, 'CodeMao Kitten Editor: Block programming platform to create games, includes micro:bit support.\nhttps://ide.codemao.cn')

    def test_commit_2(self):
        """Merge commit."""
        title, url, description = tweet_commit.get_commit_list_entry('401d6c4ee70d21dd86631eb377433b319cbb88d1')
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, 'ESP8266/ThingSpeak: Use a ESP8266 wifi module to upload data to ThingSpeak.com.\nhttps://github.com/alankrantas/pxt-ESP8266_ThingSpeak')

    def test_commit_3(self):
        """Normal commit with extra dots in the middle."""
        title, url, description = tweet_commit.get_commit_list_entry('4b661cf6bdeb22a56721bc5955eb554c736eca8c')
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, 'Hardware Simulation with QEMU: Emulation support for the micro:bit is available from QEMU 4.0 and can be used for low-level software testing and development.\nhttps://www.qemu.org/2019/05/22/microbit/')

    def test_commit_4(self):
        """Invalid awesome list entry."""
        with self.assertRaises(Exception) as context:
            title, url, description = tweet_commit.get_commit_list_entry('fa544e2c211eb47ac1cb287df5f5c09edabb2ae0')

        self.assertTrue('Could not match an awesome list entry.' in str(context.exception))

    def test_commit_5(self):
        """Normal commit with brakets."""
        title, url, description = tweet_commit.get_commit_list_entry('8a570813f0cfb3a9ebbcd9f8006e0eb8c6f11799')
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, 'SFC SNES Gamepad: Connect an SNES (Super Nintendo/Super Famicom) controller to the micro:bit.\nhttps://github.com/51bit/SFC')

    def test_commit_6(self):
        """Markdown link inside the list entry description."""
        title, url, description = tweet_commit.get_commit_list_entry('5652ef8bf0d617a3d4085429f4d39007b44ef09d')
        tweet = tweet_commit.format_tweet_msg(title, url, description)

        self.assertEqual(tweet, 'Official Swift Playgrounds: ([Source Code](https://github.com/microbit-foundation/microbit-swift-playgrounds)) Swift Playgrounds is an app for the iPad that helps teach people to code in the Swift language using interactive \'books\'.\nhttps://microbit.org/guide/swift-playgrounds/')


if __name__ == '__main__':
    project_root_dir = \
        os.path.dirname(os.path.dirname(os.path.dirname(    # Going up 3 levels
            os.path.dirname(os.path.realpath(__file__)))))  # This file folder dir
    os.chdir(project_root_dir)
    unittest.main()
