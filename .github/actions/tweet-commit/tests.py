"""Tests for post_commit."""

import io
import os
import unittest
import unittest.mock

from git import Repo

try:
    import post_commit as post_commit
except ImportError:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    import post_commit as post_commit


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
        entries = post_commit.get_commit_list_entries(commit)
        readme = post_commit.get_commit_readme(commit)
        return entries, readme

    def test_commit_1(self):
        """Normal commit."""
        entries, readme = self.get_commit_data(
            "2c58c69cd5ea09fe15726d60c40faaccc6735921"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )
        skeet = post_commit.format_msg_bluesky(
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
            "MicroPython Libraries - MB1013\n\n"
            "Module for the MB1013 ultrasonic sensor controlled via UART.\n"
            "https://github.com/liamkinne/microbit-mb1013",
        )
        self.assertEqual(
            skeet.build_text(),
            "MicroPython Libraries - MB1013\n\n"
            "Module for the MB1013 ultrasonic sensor controlled via UART.",
        )

    def test_commit_2(self):
        """Merge commit."""
        entries, readme = self.get_commit_data(
            "401d6c4ee70d21dd86631eb377433b319cbb88d1"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "MakeCode Extensions - ESP8266/ThingSpeak\n\n"
            "Use a ESP8266 wifi module to upload data to ThingSpeak.com.\n"
            "https://github.com/alankrantas/pxt-ESP8266_ThingSpeak",
        )

    def test_commit_3(self):
        """Normal commit with extra dots in the middle."""
        entries, readme = self.get_commit_data(
            "2faac881c36435b45a454989ca915f50fe919c94"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "🏗️ Projects - The Christmas Joy Spreading Machine\n\n"
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
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "Projects - Ironman Arc Reactor\n\n"
            "Choose between two different versions (Mk I and Mk II) ready to "
            "3D print and build.\n"
            "https://www.kitronik.co.uk/blog/halo-ween-ironman-arc-reactor",
        )

    def test_commit_6(self):
        """Markdown link inside the list entry description."""
        entries, readme = self.get_commit_data(
            "5652ef8bf0d617a3d4085429f4d39007b44ef09d"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )
        skeet = post_commit.format_msg_bluesky(
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
            "📱 Mobile Apps - Official Swift Playgrounds\n\n"
            "([Source Code](https://github.com/microbit-foundation/"
            "microbit-swift-playgrounds)) "
            "Swift Playgrounds is an app for the iPad that helps teach people "
            "to code in the Swift language using interactive 'books'.\n"
            "https://microbit.org/guide/swift-playgrounds/",
        )
        self.assertEqual(
            skeet.build_text(),
            "📱 Mobile Apps - Official Swift Playgrounds\n\n"
            "([Source Code](https://github.com/microbit-foundation/"
            "microbit-swift-playgrounds)) "
            "Swift Playgrounds is an app for the iPad that helps teach people "
            "to code in the Swift language using interactive 'books'.",
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
        section_0 = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet_0 = post_commit.format_msg_twitter(
            section_0,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )
        section_1 = post_commit.get_entry_section(readme, entries[1]["entry"])
        tweet_1 = post_commit.format_msg_twitter(
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
            "CAD & 3D Printing - Robottillo:bit\n\n"
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
            "CAD & 3D Printing - Battery pack holder\n\n"
            "Simple 3D printed battery pack holder for BBC #microbit.\n"
            "https://www.thingiverse.com/thing:2666671",
        )

    def test_editing_an_entry(self):
        """Editing an existing entry."""
        entries, readme = self.get_commit_data(
            "76deb0040093492197732ba1839ba52beb2e70fc"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "🆚 Visual - EduBlocks\n\n"
            "Blocks interface that provides a transitioning experience from "
            "#Scratch to #Python.\n"
            "https://app.edublocks.org",
        )

    def test_moving_an_entry(self):
        """Moving an existing entry to a different position."""
        entries, readme = self.get_commit_data(
            "a05ffd323e0cce48119ba78a35478fd18dee359c"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "MicroPython Editors - JetBrains IDEA/PyCharm IDE plugin\n\n"
            "Support for #MicroPython devices in IntelliJ IDEA and PyCharm.\n"
            "https://plugins.jetbrains.com/plugin/9777-micropython-support",
        )

    def test_msg_format_max_length(self):
        """Check that tweet formatting keeps the max characters permitted."""
        # 280 characters total, 23 for the shortned URL, 6 characters formating
        tweet = post_commit.format_msg_twitter(
            "s" * 9, "t" * 12, "u" * 23, ("d" * 229) + "."
        )
        skeet = post_commit.format_msg_bluesky(
            "s" * 7, "t" * 8, "u" * 100, ("d" * 279) + "."
        )

        self.assertEqual(len(tweet), 280)
        self.assertEqual(
            tweet,
            "sssssssss - tttttttttttt\n\n"
            "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            "dddddddddddddddddddddddddddddddddd.\n"
            "uuuuuuuuuuuuuuuuuuuuuuu",
        )
        self.assertEqual(len(skeet.build_text()), 300)
        self.assertEqual(
            skeet.build_text(),
            ("s" * 7) + " - " + ("t" * 8) + "\n\n" + ("d" * 279) + ".",
        )

    def test_msg_format_over_length(self):
        """Check that long tweet messages get truncated.

        When the tweet content exceeds the twitter character limit, it
        truncates the text to nearest word.
        """
        # 280 characters total, 23 for the shortned URL, 5 characters formating
        tweet = post_commit.format_msg_twitter(
            "s" * 9, "t" * 12, "u" * 23, "dd " * 1000
        )
        skeet = post_commit.format_msg_bluesky(
            "s" * 7, "t" * 8, "u" * 100, "dd " * 1000
        )

        self.assertEqual(len(tweet), 277)
        self.maxDiff = None
        self.assertEqual(
            tweet,
            "sssssssss - tttttttttttt\n\n"
            "dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd "
            "dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd "
            "dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd dd "
            "dd dd dd dd dd dd dd dd dd dd dd dd...\n"
            "uuuuuuuuuuuuuuuuuuuuuuu",
        )
        self.assertEqual(len(skeet.build_text()), 298)
        self.assertEqual(
            skeet.build_text(),
            ("s" * 7) + " - " + ("t" * 8) + "\n\n" + ("dd " * 91) + "dd...",
        )

    def test_long_tweet(self):
        """An entry that is too long to fit in a tweet."""
        entries, readme = self.get_commit_data(
            "8e74b6730578c24c650b375f9490a08eb7d42bdf"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )
        skeet = post_commit.format_msg_bluesky(
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
            "Miscellaneous - Radiobit, a BBC Micro:Bit RF firmware\n\n"
            "Radiobit is composed of a dedicated #MicroPython-based firmware "
            "and a set of tools allowing security researchers to sniff, "
            "receive and send data over Nordic's ShockBurst protocol, "
            "Enhanced...\n"
            "https://github.com/virtualabs/radiobit",
        )
        self.assertEqual(
            skeet.build_text(),
            "Miscellaneous - Radiobit, a BBC Micro:Bit RF firmware\n\n"
            "Radiobit is composed of a dedicated #MicroPython-based firmware "
            "and a set of tools allowing security researchers to sniff, "
            "receive and send data over Nordic's ShockBurst protocol, "
            "Enhanced ShockBurst protocol, Bluetooth Smart Link Layer and...",
        )

    def test_commit_replace_microbit_1(self):
        """Replace "microbit" for "#microbit" in description."""
        entries, readme = self.get_commit_data(
            "efeffb853b72a6df40cb2a0dad45c1b3384aba2f"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "3D Printing - Otto Robot\n\n"
            "Otto chassis for the #microbit to make a bidepad robot with a "
            "robitbit accessory.\n"
            "https://www.thingiverse.com/thing:2786066",
        )

    def test_commit_replace_microbit_2(self):
        """Replace "micro:bit" for "#microbit" in description.

        However do not touch it in the title.
        """
        entries, readme = self.get_commit_data(
            "10d7622864d9dd6cdd81546e3514bfc945af7396"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [Haxe node BBC micro:bit]"
            "(https://github.com/MatthijsKamstra/hx-node-bbc-microbit) - "
            "Control a BBC micro:bit from Node.js using BLE and the Haxe "
            "programming language.",
        )
        self.assertEqual(
            tweet,
            "Programming Tools - Haxe node BBC micro:bit\n\n"
            "Control a BBC #microbit from Node.js using BLE and the Haxe "
            "programming language.\n"
            "https://github.com/MatthijsKamstra/hx-node-bbc-microbit",
        )

    def test_commit_replace_python(self):
        """Replace "Python" for "#Python" in description."""
        entries, readme = self.get_commit_data(
            "67fb7bcb010e62982201c2c365028586e14fab70"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "🏫 Teaching Resources - micro:bit Lessons\n\n"
            "Basic lessons on #Python programming with a BBC #microbit.\n"
            "https://github.com/PhonicCanine/microbit-lessons",
        )

    def test_commit_replace_micropython_and_scratch(self):
        """Replace "micropython" -> "#MicroPython" and "Scratch" -> "#Scratch".

        Note that there isn't commits with "scratch" in lower case, so there
        isn't a test case for that.
        """
        entries, readme = self.get_commit_data(
            "b7a6767a088a47450019c5cacf9469533a087efa"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "Miscellaneous - BBC Micro:bit composer\n\n"
            "Write music and get the corresponding #microbit #MicroPython "
            "code, a tool made with #Scratch.\n"
            "https://scratch.mit.edu/projects/201592887/",
        )

    def test_commit_replace_micropython_2(self):
        """Replace "MicroPython" for "#MicroPython" in description."""
        entries, readme = self.get_commit_data(
            "96e29b83d0c7ee1c0e387a2c06aea06bf1ad8929"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "Python Programming Tools - MicroREPL\n\n"
            "A REPL client for #MicroPython running on the BBC #microbit.\n"
            "https://github.com/ntoll/microrepl",
        )

    def test_commit_replace_raspberry_pi(self):
        """Replace "Raspberry Pi" for "#RaspberryPi" in description."""
        entries, readme = self.get_commit_data(
            "e767f02151131335392957c5cf6038df9deffc6f"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "Project Collections - Raspberry Pi micro:bit Projects\n\n"
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
        section = post_commit.get_entry_section(readme, entries[1]["entry"])
        tweet = post_commit.format_msg_twitter(
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
            "C/C++ - Arduino nRF5\n\n"
            "#Arduino Core for Nordic Semiconductor nRF5 based boards, "
            "including the #microbit.\n"
            "https://github.com/sandeepmistry/arduino-nRF5/",
        )

    def test_commit_replace_makecode_1(self):
        """Replace "MakeCode" for "#MakeCode" in description."""
        entries, readme = self.get_commit_data(
            "7014b106374048fc18bb1604673e07c8208c6bc3"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 4)
        self.assertEqual(
            entries[0]["entry"],
            "\t- [MakeCode Beta](https://makecode.microbit.org/beta) - "
            "Beta version of the MakeCode editor to test the latest features.",
        )
        self.assertEqual(
            tweet,
            "🆚 Visual - MakeCode Beta\n\n"
            "Beta version of the #MakeCode editor to test the latest "
            "features.\n"
            "https://makecode.microbit.org/beta",
        )

    def test_commit_replace_makecode_2(self):
        """Replace "Makecode" for "#MakeCode" in description."""
        entries, readme = self.get_commit_data(
            "b0bb85c5d2477100e34e53c5662acc71867bf6d0"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        tweet = post_commit.format_msg_twitter(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )
        skeet = post_commit.format_msg_bluesky(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["entry"],
            "- [CCS811](https://github.com/ADataDate/pxt-airQuality) - "
            "Makecode Package for the CCS811 Air Quality Sensor.",
        )
        self.assertEqual(
            tweet,
            "MakeCode Libraries - CCS811\n\n"
            "#MakeCode Package for the CCS811 Air Quality Sensor.\n"
            "https://github.com/ADataDate/pxt-airQuality",
        )
        self.assertEqual(
            skeet.build_text(),
            "MakeCode Libraries - CCS811\n\n"
            "#MakeCode Package for the CCS811 Air Quality Sensor.",
        )

    def test_bluesky_format_with_hashtag_tags(self):
        """format_msg_bluesky properly converts hashtags to Bluesky tags."""
        # Use an existing test case that has hashtags
        entries, readme = self.get_commit_data(
            "b0bb85c5d2477100e34e53c5662acc71867bf6d0"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        skeet = post_commit.format_msg_bluesky(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        # Check that the text is correct
        self.assertEqual(
            skeet.build_text(),
            "MakeCode Libraries - CCS811\n\n"
            "#MakeCode Package for the CCS811 Air Quality Sensor.",
        )

        # Check that we have facets for the link and the hashtag
        # The link facet is for the title, and we should have a
        # tag facet for #MakeCode
        has_makecode_tag = False
        for facet in skeet._facets:
            if (
                facet.features
                and hasattr(facet.features[0], "tag")
                and facet.features[0].tag == "MakeCode"
            ):
                has_makecode_tag = True
                break

        self.assertTrue(
            has_makecode_tag, "Should have a tag facet for #MakeCode"
        )


class TestDryRun(unittest.TestCase):
    """Test that the --dry-run flag prevents posting."""

    def get_commit_data(self, commit_hash):
        """Get the list entries and readme from a commit hash."""
        repository_path = os.getcwd()
        repo = Repo(repository_path)
        commit = repo.commit(commit_hash)
        entries = post_commit.get_commit_list_entries(commit)
        readme = post_commit.get_commit_readme(commit)
        return entries, readme

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_tweet_msg_dry_run_does_not_post(self, _mock_stdout):
        """tweet_msg with dry_run=True should not create a Twitter client."""
        with unittest.mock.patch.object(
            post_commit.tweepy, "Client"
        ) as mock_client:
            post_commit.tweet_msg("Test tweet message", dry_run=True)
            mock_client.assert_not_called()

    def test_tweet_msg_dry_run_prints_message(self):
        """tweet_msg with dry_run=True should print a dry run message."""
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            post_commit.tweet_msg("Test tweet message", dry_run=True)
        output = f.getvalue()
        self.assertIn("Dry run", output)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_skeet_msg_dry_run_does_not_login(self, _mock_stdout):
        """skeet_msg with dry_run=True should not create a BlueSky client."""
        entries, readme = self.get_commit_data(
            "2c58c69cd5ea09fe15726d60c40faaccc6735921"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        skeet = post_commit.format_msg_bluesky(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        with unittest.mock.patch.object(post_commit, "Client") as mock_client:
            with unittest.mock.patch.object(
                post_commit.httpx, "get"
            ) as mock_httpx_get:
                mock_response = unittest.mock.MagicMock()
                mock_response.text = (
                    '<meta property="og:title"'
                    ' content="Test Title">'
                    '<meta property="og:description"'
                    ' content="Test Desc">'
                )
                mock_httpx_get.return_value = mock_response
                post_commit.skeet_msg(skeet, entries[0]["url"], dry_run=True)
            mock_client.assert_not_called()

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_skeet_msg_dry_run_still_fetches_og_tags(self, _mock_stdout):
        """skeet_msg with dry_run=True should still fetch OGP content."""
        entries, readme = self.get_commit_data(
            "2c58c69cd5ea09fe15726d60c40faaccc6735921"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        skeet = post_commit.format_msg_bluesky(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        with unittest.mock.patch.object(
            post_commit.httpx, "get"
        ) as mock_httpx_get:
            mock_response = unittest.mock.MagicMock()
            mock_response.text = '<meta property="og:title" content="Test">'
            mock_httpx_get.return_value = mock_response
            post_commit.skeet_msg(skeet, entries[0]["url"], dry_run=True)
            mock_httpx_get.assert_called_once_with(entries[0]["url"])

    def test_skeet_msg_dry_run_prints_embed_info(self):
        """skeet_msg dry_run=True prints embed info with OG tags."""
        from contextlib import redirect_stdout

        entries, readme = self.get_commit_data(
            "2c58c69cd5ea09fe15726d60c40faaccc6735921"
        )
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        skeet = post_commit.format_msg_bluesky(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        with unittest.mock.patch.object(
            post_commit.httpx, "get"
        ) as mock_httpx_get, unittest.mock.patch.object(
            post_commit.httpx, "head"
        ) as mock_httpx_head:
            mock_response = unittest.mock.MagicMock()
            mock_response.text = (
                '<meta property="og:title"'
                ' content="OG Title">'
                '<meta property="og:description"'
                ' content="OG Desc">'
                '<meta property="og:image"'
                ' content="https://example.com/img.png">'
            )
            mock_httpx_get.return_value = mock_response
            mock_httpx_head.return_value = unittest.mock.MagicMock()

            f = io.StringIO()
            with redirect_stdout(f):
                post_commit.skeet_msg(skeet, entries[0]["url"], dry_run=True)
            output = f.getvalue()
            self.assertIn("Dry run", output)
            self.assertIn("OG Title", output)
            self.assertIn("OG Desc", output)

    def test_parse_cli_args_dry_run_flag(self):
        """parse_cli_args should parse --dry-run flag."""
        with unittest.mock.patch(
            "sys.argv",
            [
                "prog",
                "--commit-hash",
                "abc123",
                "--trigger-keyword",
                "Tweet",
                "--dry-run",
            ],
        ):
            args = post_commit.parse_cli_args()
            self.assertTrue(args.dry_run)

    def test_parse_cli_args_no_dry_run_flag(self):
        """parse_cli_args should default dry_run to False."""
        with unittest.mock.patch(
            "sys.argv",
            ["prog", "--commit-hash", "abc123", "--trigger-keyword", "Tweet"],
        ):
            args = post_commit.parse_cli_args()
            self.assertFalse(args.dry_run)


class TestOgTagFixes(unittest.TestCase):
    """Test OG tag parsing fixes in skeet_msg.

    These tests mock httpx to simulate the specific OG tag issues
    found in commits ed36386, 6be256b, and 8894326.
    """

    def get_commit_data(self, commit_hash):
        """Get the list entries and readme from a commit hash."""
        repository_path = os.getcwd()
        repo = Repo(repository_path)
        commit = repo.commit(commit_hash)
        entries = post_commit.get_commit_list_entries(commit)
        readme = post_commit.get_commit_readme(commit)
        return entries, readme

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_og_image_alt_before_og_image(self, mock_stdout):
        """og:image:alt before og:image should not confuse parsing.

        Commit 8894326: The page has og:image:alt before og:image,
        so a substring match on 'og:image' would match the alt tag
        first and return its content instead of the actual image URL.
        """
        entries, readme = self.get_commit_data("8894326")
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        skeet = post_commit.format_msg_bluesky(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        og_html = (
            '<meta property="og:image:alt"'
            ' content="Oak National Academy">'
            '<meta property="og:title"'
            ' content="Physical computing">'
            '<meta property="og:description"'
            ' content="Free lessons">'
            '<meta property="og:image"'
            ' content="https://example.com/real-image.png">'
        )
        with unittest.mock.patch.object(
            post_commit.httpx, "get"
        ) as mock_get, unittest.mock.patch.object(
            post_commit.httpx, "head"
        ) as mock_head:
            mock_page = unittest.mock.MagicMock()
            mock_page.text = og_html
            mock_get.return_value = mock_page
            mock_head.return_value = unittest.mock.MagicMock()

            post_commit.skeet_msg(skeet, entries[0]["url"], dry_run=True)

        output = mock_stdout.getvalue()
        # Should find the real og:image, not the og:image:alt
        self.assertIn("https://example.com/real-image.png", output)
        self.assertNotIn("Image URL: Oak National Academy", output)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_og_image_relative_url(self, mock_stdout):
        """Relative og:image URLs should be resolved to absolute.

        Commit ed36386: The og:image content is a relative path like
        '/packs/media/images/courses/courses-xxx.png' which needs to
        be resolved against the page URL.
        """
        entries, readme = self.get_commit_data("ed36386")
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        skeet = post_commit.format_msg_bluesky(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )
        page_url = entries[0]["url"]

        og_html = (
            '<meta property="og:title"'
            ' content="Teaching programming">'
            '<meta property="og:description"'
            ' content="Explore how to use the micro:bit">'
            '<meta property="og:image"'
            ' content="/packs/media/images/courses.png">'
        )
        with unittest.mock.patch.object(
            post_commit.httpx, "get"
        ) as mock_get, unittest.mock.patch.object(
            post_commit.httpx, "head"
        ) as mock_head:
            mock_page = unittest.mock.MagicMock()
            mock_page.text = og_html
            mock_get.return_value = mock_page
            mock_head.return_value = unittest.mock.MagicMock()

            post_commit.skeet_msg(skeet, page_url, dry_run=True)

        output = mock_stdout.getvalue()
        # The relative URL should be resolved to an absolute URL
        self.assertIn(
            "https://teachcomputing.org/packs/media/images/courses.png",
            output,
        )
        # Should NOT contain just the relative path
        self.assertNotIn("Image URL: /packs/media", output)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_og_tags_page_fetch_error(self, mock_stdout):
        """Page returning 403/404 should not crash the script.

        Commit 6be256b: The page URL returns a 403 Forbidden,
        so _get_og_tags should handle the error gracefully and
        return None values instead of raising an exception.
        """
        entries, readme = self.get_commit_data("6be256b")
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        skeet = post_commit.format_msg_bluesky(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        with unittest.mock.patch.object(post_commit.httpx, "get") as mock_get:
            mock_response = unittest.mock.MagicMock()
            mock_response.raise_for_status.side_effect = (
                post_commit.httpx.HTTPStatusError(
                    "403 Forbidden",
                    request=unittest.mock.MagicMock(),
                    response=unittest.mock.MagicMock(),
                )
            )
            mock_get.return_value = mock_response

            # Should not raise an exception
            post_commit.skeet_msg(skeet, entries[0]["url"], dry_run=True)

        output = mock_stdout.getvalue()
        self.assertIn("Dry run", output)
        self.assertIn("Warning", output)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_og_image_inaccessible(self, mock_stdout):
        """Inaccessible og:image URL should be set to None.

        When the og:image URL returns a 403/404 on HEAD request,
        the image should be set to None and a warning printed.
        """
        entries, readme = self.get_commit_data("8894326")
        section = post_commit.get_entry_section(readme, entries[0]["entry"])
        skeet = post_commit.format_msg_bluesky(
            section,
            entries[0]["title"],
            entries[0]["url"],
            entries[0]["description"],
        )

        og_html = (
            '<meta property="og:title"'
            ' content="Test Title">'
            '<meta property="og:description"'
            ' content="Test Desc">'
            '<meta property="og:image"'
            ' content="https://example.com/broken.png">'
        )
        with unittest.mock.patch.object(post_commit.httpx, "get") as mock_get:
            mock_page = unittest.mock.MagicMock()
            mock_page.text = og_html

            def get_side_effect(url, **kwargs):
                if url == "https://example.com/broken.png":
                    raise post_commit.httpx.HTTPStatusError(
                        "404 Not Found",
                        request=unittest.mock.MagicMock(),
                        response=unittest.mock.MagicMock(),
                    )
                return mock_page

            mock_get.side_effect = get_side_effect

            post_commit.skeet_msg(skeet, entries[0]["url"], dry_run=True)

        output = mock_stdout.getvalue()
        self.assertIn("Warning: og:image URL not accessible", output)
        self.assertIn("Image URL: https://example.com/broken.png", output)
        self.assertIn("Image type: None", output)


if __name__ == "__main__":
    # Project root is up 3 levels from this file
    project_root_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        )
    )
    os.chdir(project_root_dir)
    unittest.main()
