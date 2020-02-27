"""Tests for tweet_commit."""
import os
import unittest

from git import Repo

try:
    import tweet_commit
except ImportError:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    import tweet_commit


class TestCommitTweet(unittest.TestCase):
    """Test tweet parsing from commits located in this repo.

    This tests depend on the git history from the awesome-microbit repo, not
    a great way to write test, as we could have mock a the git library, but
    this is quick way to run the tests with real examples.
    """

    def get_commit_data(self, commit_hash):
        """Get the list entires and readme from a commit hash."""
        repository_path = os.getcwd()
        repo = Repo(repository_path)
        commit = repo.commit(commit_hash)
        entries = tweet_commit.get_commit_list_entries(commit)
        readme = tweet_commit.get_commit_readme(commit)
        return entries, readme

    def test_commit_1(self):
        """Normal commit."""
        entries, readme = self.get_commit_data(
            "2c58c69cd5ea09fe15726d60c40faaccc6735921"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [MB1013](https://github.com/liamkinne/microbit-mb1013) - "
            "Module for the MB1013 ultrasonic sensor controlled via UART.",
        )
        self.assertEqual(
            tweet,
            "MicroPython Libraries - MB1013\n"
            "Module for the MB1013 ultrasonic sensor controlled via UART.\n"
            "https://github.com/liamkinne/microbit-mb1013",
        )

    def test_commit_2(self):
        """Merge commit."""
        entries, readme = self.get_commit_data(
            "401d6c4ee70d21dd86631eb377433b319cbb88d1"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [ESP8266/ThingSpeak]"
            "(https://github.com/alankrantas/pxt-ESP8266_ThingSpeak) - "
            "Use a ESP8266 wifi module to upload data to ThingSpeak.com.",
        )
        self.assertEqual(
            tweet,
            "MakeCode Extensions - ESP8266/ThingSpeak\n"
            "Use a ESP8266 wifi module to upload data to ThingSpeak.com.\n"
            "https://github.com/alankrantas/pxt-ESP8266_ThingSpeak",
        )

    def test_commit_3(self):
        """Normal commit with extra dots in the middle."""
        entries, readme = self.get_commit_data(
            "2faac881c36435b45a454989ca915f50fe919c94"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [The Christmas Joy Spreading Machine]"
            "(https://www.hackster.io/balearicdynamics/"
            "the-christmas-joy-spreading-machine-3d3559) - "
            "Project inside a box representing a metaphor of the most popular "
            "Christmas symbols. Maybe it's a bit distopyc but it moves, "
            "lights and reacts to music.",
        )
        self.assertEqual(
            tweet,
            "🏗️ Projects - The Christmas Joy Spreading Machine\n"
            "Project inside a box representing a metaphor of the most popular "
            "Christmas symbols. Maybe it's a bit distopyc but it moves, "
            "lights and reacts to music.\n"
            "https://www.hackster.io/balearicdynamics/"
            "the-christmas-joy-spreading-machine-3d3559",
        )

    def test_commit_5(self):
        """Normal commit with brackets."""
        entries, readme = self.get_commit_data(
            "d8eaa108e6fbb635f282f341e64b7b36507f0788"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [Ironman Arc Reactor]"
            "(https://www.kitronik.co.uk/blog/"
            "halo-ween-ironman-arc-reactor) - "
            "Choose between two different versions (Mk I and Mk II) ready to "
            "3D print and build.",
        )
        self.assertEqual(
            tweet,
            "Projects - Ironman Arc Reactor\n"
            "Choose between two different versions (Mk I and Mk II) ready to "
            "3D print and build.\n"
            "https://www.kitronik.co.uk/blog/halo-ween-ironman-arc-reactor",
        )

    def test_commit_6(self):
        """Markdown link inside the list entry description."""
        entries, readme = self.get_commit_data(
            "5652ef8bf0d617a3d4085429f4d39007b44ef09d"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [Official Swift Playgrounds]"
            "(https://microbit.org/guide/swift-playgrounds/) - ([Source Code]"
            "(https://github.com/microbit-foundation/"
            "microbit-swift-playgrounds)) "
            "Swift Playgrounds is an app for the iPad that helps teach people "
            "to code in the Swift language using interactive 'books'.",
        )
        self.assertEqual(
            tweet,
            "📱 Mobile Apps - Official Swift Playgrounds\n"
            "([Source Code](https://github.com/microbit-foundation/"
            "microbit-swift-playgrounds)) "
            "Swift Playgrounds is an app for the iPad that helps teach people "
            "to code in the Swift language using interactive 'books'.\n"
            "https://microbit.org/guide/swift-playgrounds/",
        )

    def test_invalid_no_description(self):
        """Invalid awesome list entry: No description."""
        with self.assertRaises(Exception) as context:
            entries, readme = self.get_commit_data(
                "fa544e2c211eb47ac1cb287df5f5c09edabb2ae0"
            )

        self.assertTrue(
            "Could not match an Awesome List entry." in str(context.exception)
        )

    def test_multiple_entries(self):
        """A single commit with multiple list entries."""
        entries, readme = self.get_commit_data(
            "749861108e6f65751c4ec0927ef40d495e56dad5"
        )
        section_0 = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet_0 = tweet_commit.format_tweet_msg(
            section_0,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )
        section_1 = tweet_commit.get_entry_section(readme, entries[1]["entry"])
        tweet_1 = tweet_commit.format_tweet_msg(
            section_1,
            entries[1]["title"],
            entries[1]["url"],
            entries[1]["description"],
        )

        self.assertEqual(len(entries), 2)
        self.assertEqual(
            entries[0]["entry"],
            "- [Robottillo:bit]"
            "(https://www.myminifactory.com/object/robottillo-bit-46478) - "
            "A 3D printed case which looks like a small robot. Two versions "
            "available, with a rear protective cover or with a perforated "
            "cover for the pins.",
        )
        self.assertEqual(
            tweet_0,
            "CAD & 3D Printing - Robottillo:bit\n"
            "A 3D printed case which looks like a small robot. Two versions "
            "available, with a rear protective cover or with a perforated "
            "cover for the pins.\n"
            "https://www.myminifactory.com/object/robottillo-bit-46478",
        )
        self.assertEqual(
            entries[1]["entry"],
            "- [Battery pack holder]"
            "(https://www.thingiverse.com/thing:2666671) - "
            "Simple 3D printed battery pack holder for BBC micro:bit.",
        )
        self.assertEqual(
            tweet_1,
            "CAD & 3D Printing - Battery pack holder\n"
            "Simple 3D printed battery pack holder for BBC #microbit.\n"
            "https://www.thingiverse.com/thing:2666671",
        )

    def test_editing_an_entry(self):
        """Editing an existing entry."""
        entries, readme = self.get_commit_data(
            "76deb0040093492197732ba1839ba52beb2e70fc"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [EduBlocks](https://app.edublocks.org) - Blocks interface that "
            "provides a transitioning experience from Scratch to Python.",
        )
        self.assertEqual(
            tweet,
            "🆚 Visual - EduBlocks\n"
            "Blocks interface that provides a transitioning experience from "
            "#Scratch to #Python.\n"
            "https://app.edublocks.org",
        )

    def test_moving_an_entry(self):
        """Moving an existing entry to a different position."""
        entries, readme = self.get_commit_data(
            "a05ffd323e0cce48119ba78a35478fd18dee359c"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [JetBrains IDEA/PyCharm IDE plugin]"
            "(https://plugins.jetbrains.com/plugin/9777-micropython-support) "
            "- Support for MicroPython devices in IntelliJ IDEA and PyCharm.",
        )
        self.assertEqual(
            tweet,
            "MicroPython Editors - JetBrains IDEA/PyCharm IDE plugin\n"
            "Support for #MicroPython devices in IntelliJ IDEA and PyCharm.\n"
            "https://plugins.jetbrains.com/plugin/9777-micropython-support",
        )

    def test_msg_format_max_length(self):
        """Check that tweet formatting keeps the max characters permitted."""
        # 280 characters total, 23 for the shortned URL, 5 characters formating
        tweet = tweet_commit.format_tweet_msg(
            "s" * 9, "t" * 12, "u" * 23, ("d" * 230) + "."
        )

        self.assertEqual(len(tweet), 280)
        self.assertEqual(
            tweet,
            "sssssssss - tttttttttttt\n"
            "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            "ddddddddddddddddddddddddddddddddddd.\n"
            "uuuuuuuuuuuuuuuuuuuuuuu",
        )

    def test_msg_format_over_length(self):
        """Check that long tweet messages get truncated.

        When the tweet content exceeds the twitter character limit, it
        truncates the text to nearest word.
        """
        # 280 characters total, 23 for the shortned URL, 4 characters formating
        tweet = tweet_commit.format_tweet_msg(
            "s" * 9, "t" * 12, "u" * 23, "dd " * 1000
        )

        self.assertEqual(len(tweet), 279)
        self.maxDiff = None
        self.assertEqual(
            tweet,
            "sssssssss - tttttttttttt\n"
            "dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd "
            "dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd "
            "dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd "
            "dd dd dd dd dd dd dd dd dd dd dd dd dd...\n"
            "uuuuuuuuuuuuuuuuuuuuuuu",
        )

    def test_long_tweet(self):
        """An entry that is too long to fit in a tweet."""
        entries, readme = self.get_commit_data(
            "8e74b6730578c24c650b375f9490a08eb7d42bdf"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.maxDiff = None
        self.assertEqual(
            entries[0]["entry"],
            "- [Radiobit, a BBC Micro:Bit RF firmware]"
            "(https://github.com/virtualabs/radiobit) - "
            "Radiobit is composed of a dedicated Micropython-based firmware "
            "and a set of tools allowing security researchers to sniff, "
            "receive and send data over Nordic's ShockBurst protocol, "
            "Enhanced ShockBurst protocol, Bluetooth Smart Link Layer and "
            "sniff raw 2.4GHz GFSK demodulated data.",
        )
        self.assertEqual(
            tweet,
            "Miscellaneous - Radiobit, a BBC Micro:Bit RF firmware\n"
            "Radiobit is composed of a dedicated #MicroPython-based firmware "
            "and a set of tools allowing security researchers to sniff, "
            "receive and send data over Nordic's ShockBurst protocol, "
            "Enhanced...\n"
            "https://github.com/virtualabs/radiobit",
        )

    def test_commit_replace_microbit_1(self):
        """Replace "microbit" for "#microbit" in description."""
        entries, readme = self.get_commit_data(
            "efeffb853b72a6df40cb2a0dad45c1b3384aba2f"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [Otto Robot](https://www.thingiverse.com/thing:2786066) - "
            "Otto chassis for the microbit to make a bidepad robot with a "
            "robitbit accessory.",
        )
        self.assertEqual(
            tweet,
            "3D Printing - Otto Robot\n"
            "Otto chassis for the #microbit to make a bidepad robot with a "
            "robitbit accessory.\n"
            "https://www.thingiverse.com/thing:2786066",
        )

    def test_commit_replace_microbit_2(self):
        """Replace "micro:bit" for "#microbit" in description.

        However do not touch it in the title.
        """
        entries, readme = self.get_commit_data(
            "5a04d4c8a4d51c10ee87a0d69656bb1c695447f1"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [Grade 10 micro:bit Tutorials]"
            "(https://www.youtube.com/playlist?list="
            "PLo6KSCBvKXc92f7p8ONiBeWAJKIqNpKlr) - "
            "Collection of short videos showing how to use micro:bit MakeCode "
            "blocks and features.",
        )
        self.assertEqual(
            tweet,
            "🎥 Videos - Grade 10 micro:bit Tutorials\n"
            "Collection of short videos showing how to use #microbit MakeCode "
            "blocks and features.\n"
            "https://www.youtube.com/playlist?list="
            "PLo6KSCBvKXc92f7p8ONiBeWAJKIqNpKlr",
        )

    def test_commit_replace_python(self):
        """Replace "Python" for "#Python" in description."""
        entries, readme = self.get_commit_data(
            "67fb7bcb010e62982201c2c365028586e14fab70"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [micro:bit Lessons]"
            "(https://github.com/PhonicCanine/microbit-lessons) - "
            "Basic lessons on Python programming with a BBC micro:bit.",
        )
        self.assertEqual(
            tweet,
            "🏫 Teaching Resources - micro:bit Lessons\n"
            "Basic lessons on #Python programming with a BBC #microbit.\n"
            "https://github.com/PhonicCanine/microbit-lessons",
        )

    def test_commit_replace_micropython_1(self):
        """Replace "micropython" -> "#MicroPython" and "Scratch" -> "#Scratch".

        Note that there isn't commits with "scratch" in lower case, so there
        isn't a test case for that.
        """
        entries, readme = self.get_commit_data(
            "b7a6767a088a47450019c5cacf9469533a087efa"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [BBC Micro:bit composer]"
            "(https://scratch.mit.edu/projects/201592887/) - "
            "Write music and get the corresponding micro:bit micropython "
            "code, a tool made with Scratch.",
        )
        self.assertEqual(
            tweet,
            "Miscellaneous - BBC Micro:bit composer\n"
            "Write music and get the corresponding #microbit #MicroPython "
            "code, a tool made with #Scratch.\n"
            "https://scratch.mit.edu/projects/201592887/",
        )

    def test_commit_replace_micropython_2(self):
        """Replace "MicroPython" for "#MicroPython" in description."""
        entries, readme = self.get_commit_data(
            "96e29b83d0c7ee1c0e387a2c06aea06bf1ad8929"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [MicroREPL](https://github.com/ntoll/microrepl) - "
            "A REPL client for MicroPython running on the BBC micro:bit.",
        )
        self.assertEqual(
            tweet,
            "Python Programming Tools - MicroREPL\n"
            "A REPL client for #MicroPython running on the BBC #microbit.\n"
            "https://github.com/ntoll/microrepl",
        )

    def test_commit_replace_raspberry_pi(self):
        """Replace "Raspberry Pi" for "#RaspberryPi" in description."""
        entries, readme = self.get_commit_data(
            "e767f02151131335392957c5cf6038df9deffc6f"
        )
        section = tweet_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [Raspberry Pi micro:bit Projects]"
            "(https://projects.raspberrypi.org/en/projects?technologies%5B%5D="
            "microbit) - "
            "Collection of Raspberry Pi and micro:bit projects from the "
            "Raspberry Pi Foundation.",
        )
        self.assertEqual(
            tweet,
            "Project Collections - Raspberry Pi micro:bit Projects\n"
            "Collection of #RaspberryPi and #microbit projects from the "
            "#RaspberryPi Foundation.\n"
            "https://projects.raspberrypi.org/en/projects?technologies%5B%5D="
            "microbit",
        )

    def test_commit_replace_arduino(self):
        """Replace "Arduino" for "#Arduino" in description."""
        entries, readme = self.get_commit_data(
            "ac8791c560dcfffdfa80fc09dfa218556c98bebe"
        )
        section = tweet_commit.get_entry_section(readme, entries[1]["entry"])
        tweet = tweet_commit.format_tweet_msg(
            section,
            entries[1]["title"],
            entries[1]["url"],
            entries[1]["description"],
        )

        self.assertEqual(len(entries), 2)
        self.assertEqual(
            entries[1]["entry"],
            "- [Arduino nRF5]"
            "(https://github.com/sandeepmistry/arduino-nRF5/) - "
            "Arduino Core for Nordic Semiconductor nRF5 based boards, "
            "including the micro:bit.",
        )
        self.assertEqual(
            tweet,
            "C/C++ - Arduino nRF5\n"
            "#Arduino Core for Nordic Semiconductor nRF5 based boards, "
            "including the #microbit.\n"
            "https://github.com/sandeepmistry/arduino-nRF5/",
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
