"""Tests for tweet_commit."""
import os
import unittest

try:
    import tweet_commit
except ImportError:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    import tweet_commit


class TestCommitTweet(unittest.TestCase):
    """Test tweet parsing from commits located in this repo.

    This tests depend on the git history from the awesome-microbit repo, not
    a great way to write test, as we could have mock a the git library, but
    this is quick way to get this tested.
    """

    def test_commit_1(self):
        """Normal commit."""
        entries = tweet_commit.get_commit_list_entries(
            "2c58c69cd5ea09fe15726d60c40faaccc6735921"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "MB1013 - Module for the MB1013 ultrasonic sensor controlled via "
            "UART.\nhttps://github.com/liamkinne/microbit-mb1013",
        )

    def test_commit_2(self):
        """Merge commit."""
        entries = tweet_commit.get_commit_list_entries(
            "401d6c4ee70d21dd86631eb377433b319cbb88d1"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "ESP8266/ThingSpeak - Use a ESP8266 wifi module to upload data to "
            "ThingSpeak.com.\n"
            "https://github.com/alankrantas/pxt-ESP8266_ThingSpeak",
        )

    def test_commit_3(self):
        """Normal commit with extra dots in the middle."""
        entries = tweet_commit.get_commit_list_entries(
            "2faac881c36435b45a454989ca915f50fe919c94"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "The Christmas Joy Spreading Machine - Project inside a box "
            "representing a metaphor of the most popular Christmas symbols. "
            "Maybe it's a bit distopyc but it moves, lights and reacts to "
            "music.\nhttps://www.hackster.io/balearicdynamics/the-christmas-"
            "joy-spreading-machine-3d3559",
        )

    def test_commit_5(self):
        """Normal commit with brackets."""
        entries = tweet_commit.get_commit_list_entries(
            "d8eaa108e6fbb635f282f341e64b7b36507f0788"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "Ironman Arc Reactor - Choose between two different versions (Mk "
            "I and Mk II) ready to 3D print and build.\n"
            "https://www.kitronik.co.uk/blog/halo-ween-ironman-arc-reactor",
        )

    def test_commit_6(self):
        """Markdown link inside the list entry description."""
        entries = tweet_commit.get_commit_list_entries(
            "5652ef8bf0d617a3d4085429f4d39007b44ef09d"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "Official Swift Playgrounds - ([Source Code](https://github.com/"
            "microbit-foundation/microbit-swift-playgrounds)) Swift "
            "Playgrounds is an app for the iPad that helps teach people to "
            "code in the Swift language using interactive 'books'.\n"
            "https://microbit.org/guide/swift-playgrounds/",
        )

    def test_invalid_no_description(self):
        """Invalid awesome list entry: No description."""
        with self.assertRaises(Exception) as context:
            tweet_commit.get_commit_list_entries(
                "fa544e2c211eb47ac1cb287df5f5c09edabb2ae0"
            )

        self.assertTrue(
            "Could not match an Awesome List entry." in str(context.exception)
        )

    def test_multiple_entries(self):
        """A single commit with multiple list entries."""
        entries = tweet_commit.get_commit_list_entries(
            "749861108e6f65751c4ec0927ef40d495e56dad5"
        )
        tweet_0 = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )
        tweet_1 = tweet_commit.format_tweet_msg(
            entries[1]["title"], entries[1]["url"], entries[1]["description"]
        )

        self.assertEqual(len(entries), 2)
        self.assertEqual(
            tweet_0,
            "Robottillo:bit - A 3D printed case which looks like a small "
            "robot. Two versions available, with a rear protective cover or "
            "with a perforated cover for the pins.\n"
            "https://www.myminifactory.com/object/robottillo-bit-46478",
        )
        self.assertEqual(
            tweet_1,
            "Battery pack holder - Simple 3D printed battery pack holder for "
            "BBC #microbit.\nhttps://www.thingiverse.com/thing:2666671",
        )

    def test_editing_an_entry(self):
        """Editing an existing entry."""
        entries = tweet_commit.get_commit_list_entries(
            "76deb0040093492197732ba1839ba52beb2e70fc"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "EduBlocks - Blocks interface that provides a transitioning "
            "experience from #Scratch to #Python.\nhttps://app.edublocks.org",
        )

    def test_moving_an_entry(self):
        """Moving an existing entry to a different position."""
        entries = tweet_commit.get_commit_list_entries(
            "a05ffd323e0cce48119ba78a35478fd18dee359c"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "JetBrains IDEA/PyCharm IDE plugin - Support for #MicroPython "
            "devices in IntelliJ IDEA and PyCharm.\n"
            "https://plugins.jetbrains.com/plugin/9777-micropython-support",
        )

    def test_msg_format_max_length(self):
        """Check that tweet formatting keeps the max characters permitted."""
        # 280 characters total, 23 for the shortned URL, 4 characters formating
        tweet = tweet_commit.format_tweet_msg(
            "t" * 12, "u" * 23, ("d" * 240) + "."
        )

        self.assertEqual(len(tweet), 280)
        self.assertEqual(
            tweet,
            "tttttttttttt - dddddddddddddddddddddddddddddddddddddddddddddddddd"
            "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd.\n"
            "uuuuuuuuuuuuuuuuuuuuuuu",
        )

    def test_msg_format_over_length(self):
        """Check that long tweet messages get truncated.

        When the tweet content exceeds the twitter character limit, it
        truncates the text to nearest word.
        """
        # 280 characters total, 23 for the shortned URL, 4 characters formating
        tweet = tweet_commit.format_tweet_msg("t" * 12, "u" * 23, " dd" * 1000)

        self.assertEqual(len(tweet), 279)
        self.assertEqual(
            tweet,
            "tttttttttttt -  dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd "
            "dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd "
            "dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd "
            "dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd "
            "dd...\nuuuuuuuuuuuuuuuuuuuuuuu",
        )

    def test_long_tweet(self):
        """An entry that is too long to fit in a tweet."""
        entries = tweet_commit.get_commit_list_entries(
            "8e74b6730578c24c650b375f9490a08eb7d42bdf"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.maxDiff = None
        self.assertEqual(
            tweet,
            "Radiobit, a BBC Micro:Bit RF firmware - Radiobit is composed of "
            "a dedicated #MicroPython-based firmware and a set of tools "
            "allowing security researchers to sniff, receive and send data "
            "over Nordic's ShockBurst protocol, Enhanced ShockBurst "
            "protocol,...\nhttps://github.com/virtualabs/radiobit",
        )

    def test_commit_replace_microbit_1(self):
        """Replace "microbit" for "#microbit" in description."""
        entries = tweet_commit.get_commit_list_entries(
            "efeffb853b72a6df40cb2a0dad45c1b3384aba2f"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "Otto Robot - Otto chassis for the #microbit to make a bidepad "
            "robot with a robitbit accessory.\n"
            "https://www.thingiverse.com/thing:2786066",
        )

    def test_commit_replace_microbit_2(self):
        """Replace "micro:bit" for "#microbit" in description.

        However do not touch it in the title.
        """
        entries = tweet_commit.get_commit_list_entries(
            "5a04d4c8a4d51c10ee87a0d69656bb1c695447f1"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "Grade 10 micro:bit Tutorials - Collection of short videos "
            "showing how to use #microbit MakeCode blocks and features.\n"
            "https://www.youtube.com/playlist?list="
            "PLo6KSCBvKXc92f7p8ONiBeWAJKIqNpKlr",
        )

    def test_commit_replace_python(self):
        """Replace "Python" for "#Python" in description."""
        entries = tweet_commit.get_commit_list_entries(
            "67fb7bcb010e62982201c2c365028586e14fab70"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "micro:bit Lessons - Basic lessons on #Python programming with a "
            "BBC #microbit.\nhttps://github.com/PhonicCanine/microbit-lessons",
        )

    def test_commit_replace_micropython_1(self):
        """Replace "micropython" -> "#MicroPython" and "Scratch" -> "#Scratch".

        Note that there isn't commits with "scratch" in lower case, so there
        isn't a test case for that.
        """
        entries = tweet_commit.get_commit_list_entries(
            "b7a6767a088a47450019c5cacf9469533a087efa"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "BBC Micro:bit composer - Write music and get the corresponding "
            "#microbit #MicroPython code, a tool made with #Scratch.\n"
            "https://scratch.mit.edu/projects/201592887/",
        )

    def test_commit_replace_micropython_2(self):
        """Replace "MicroPython" for "#MicroPython" in description."""
        entries = tweet_commit.get_commit_list_entries(
            "96e29b83d0c7ee1c0e387a2c06aea06bf1ad8929"
        )
        tweet = tweet_commit.format_tweet_msg(
            entries[0]["title"], entries[0]["url"], entries[0]["description"]
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            tweet,
            "MicroREPL - A REPL client for #MicroPython running on the BBC "
            "#microbit.\nhttps://github.com/ntoll/microrepl",
        )


if __name__ == "__main__":
    # Project root is up 3 levels from this file
    project_root_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        )
    )
    os.chdir(project_root_dir)
    unittest.main()
