import entry_point
import unittest


class TestCommitTweet(unittest.TestCase):
    """Tests that commits in this repo are parsed correctly.

    This tests depend on the git history from the awesome-microbit repo, not
    a great way to test this (we could mock a the git library), but a quick
    way to get this tested.
    """

    def test_commit_1(self):
        """Normal commit."""
        _, entry_title, entry_url, entry_description = entry_point.get_commit_info('f219e79ff490f784d8a6bb8807149034dded68a8')
        tweet = entry_point.format_tweet_msg(entry_title, entry_url, entry_description)
        self.assertEqual(tweet, 'CodeMao Kitten Editor: Block programming platform to create games, includes micro:bit support.\nhttps://ide.codemao.cn')

    def test_commit_2(self):
        """Merge commit."""
        _, entry_title, entry_url, entry_description = entry_point.get_commit_info('401d6c4ee70d21dd86631eb377433b319cbb88d1')
        tweet = entry_point.format_tweet_msg(entry_title, entry_url, entry_description)
        self.assertEqual(tweet, 'ESP8266/ThingSpeak: Use a ESP8266 wifi module to upload data to ThingSpeak.com.\nhttps://github.com/alankrantas/pxt-ESP8266_ThingSpeak')

    def test_commit_3(self):
        """Normal commit with extra dots in the middle."""
        _, entry_title, entry_url, entry_description = entry_point.get_commit_info('4b661cf6bdeb22a56721bc5955eb554c736eca8c')
        tweet = entry_point.format_tweet_msg(entry_title, entry_url, entry_description)
        self.assertEqual(tweet, 'Hardware Simulation with QEMU: Emulation support for the micro:bit is available from QEMU 4.0 and can be used for low-level software testing and development.\nhttps://www.qemu.org/2019/05/22/microbit/')

    def test_commit_4(self):
        """Invalid awesome list entry."""
        _, entry_title, entry_url, entry_description = entry_point.get_commit_info('fa544e2c211eb47ac1cb287df5f5c09edabb2ae0')
        tweet = entry_point.format_tweet_msg(entry_title, entry_url, entry_description)
        self.assertIsNone(entry_title)
        self.assertIsNone(entry_url)
        self.assertIsNone(entry_description)

    def test_commit_5(self):
        """Normal commit with brakets."""
        _, entry_title, entry_url, entry_description = entry_point.get_commit_info('8a570813f0cfb3a9ebbcd9f8006e0eb8c6f11799')
        tweet = entry_point.format_tweet_msg(entry_title, entry_url, entry_description)
        self.assertEqual(tweet, 'SFC SNES Gamepad: Connect an SNES (Super Nintendo/Super Famicom) controller to the micro:bit.\nhttps://github.com/51bit/SFC')

    def test_commit_6(self):
        """Markdown inside the list entry description."""
        _, entry_title, entry_url, entry_description = entry_point.get_commit_info('5652ef8bf0d617a3d4085429f4d39007b44ef09d')
        tweet = entry_point.format_tweet_msg(entry_title, entry_url, entry_description)
        self.assertEqual(tweet, 'Official Swift Playgrounds: ([Source Code](https://github.com/microbit-foundation/microbit-swift-playgrounds)) Swift Playgrounds is an app for the iPad that helps teach people to code in the Swift language using interactive \'books\'.\nhttps://microbit.org/guide/swift-playgrounds/')


if __name__ == '__main__':
    unittest.main()
