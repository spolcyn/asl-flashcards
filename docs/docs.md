# ASL Flashcards User Guide


## Purpose

The ASL flashcards app makes it easy to split a class vocabulary video into
individual videos that correspond to the vocabularly list it was created for.

It is meant to help create flashcards for the [Anki](https://apps.ankiweb.net/)
flashcard software. Support for learning about how to use Anki is not (and will
not be) offered in these docs. Those interested are encouraged to look at the
many resources elsewhere on the Internet.


## Tutorial

### Required Materials

1. Video file with instructor signing each vocabulary word
2. CSV vocabularly list file containing the start time of each word and the English translation
   of what is being signed. See [Format Specification](#format-spec) for more
   details.

### Step 1: Creating the CSV Vocabulary List File

The recommended way to do this is using VLC. Before proceeding, follow the
instructions in the [appendix](#appendix-a) to set up VLC for this step, if you
haven't already.

1. Create the vocabulary list in a spreadsheet

    1. Using a program like Microsoft Excel, Google Sheets, Numbers, etc., make
       a spreadsheet with columns according to the [Format
       Specification](#format-spec).
    2. In the `word` column, enter each of your vocabulary words (one per row)
       in the order they appear in the vocabulary video.
    3. At the end, your spreadsheet should look like [the
       example](#rendered-vocabulary-csv), but with all columns other than
       `word` empty.

2. Open your video in VLC.

    1. Play the video until the first word starts. As soon as the motion begins,
       pause the video, and in the row in your spreadsheet corresponding to the
       word that is about to be signed, write down the timestamp (in seconds)
       shown by the VLC plugin on the video. For example, you might write down
       `1.902` in your spreadsheet next to the first word.
    2. Continue playing/pausing the video until you have a starting timestamp
       for all signs in the video. Be careful not to put the starting timestamp
       too late, or your flashcard's sign video will be cut off!
    3. When complete, export your spreadsheet as a CSV file. Google `export as
       CSV <your spreadsheet program>` to find resources on how to do so if you
       don't know how, e.g., `export as CSV excel`.

<a name="using-app"></a>
### Step 2: Using the ASL Flashcards App

Once you've finished your CSV vocabulary list file, you're ready to use the app.
This should be the easiest part!

1. Under `Vocab and Timing List Upload`, upload your CSV vocabulary list file.
   Your file will be validated, and a preview of your file will appear.
2. Under `Video Upload`, upload the vocabulary video corresponding to your
   vocabulary list.

The video will then be split into one video for each word. This could take some
time, especially if your video is long. After the split is complete, you can
download all your word videos at once.

You can also download an Anki `apkg` (Anki Package) file that has all the
necessary data in the proper format to import cards in bulk to Anki. See
[Importing Flashcards to Anki](#anki-import) for more details.

<a name="anki-import"></a>
### Step 3: Importing Flashcards to Anki

After making your flashcards, download the Anki Package file from the app. Now,
double click the file. It should automatically open in Anki. If a double click
doesn't work, use the `Import` button (on macOS, it's under `File -> Import`)
and select the `.apkg` file you've just downloaded.

You should now see a deck called "ASL Anki" in your Anki deck list. Whenever you
use the app in the future, you can continue to download the `.apkg` file from
the app, and when you import it, all of your new flashcards will go straight
into that deck.

Congratulations! You're all done. Time to go study.

#### Expert/Manual Import Mode

The following steps are for manual CSV and media imports. While this can give
you additional flexibility in your import, for most users, it's highly
recommended to use the `apkg` import method described above instead!

#### Step 3.0 (Expert/Manual): Download Files

After creating your flashcards with the [previous step](#using-app), download
the ZIP file containing all the split videos and the CSV to import to Anki. The
following steps will tell you how to use them.

#### Step 3.1 (Expert/Manual): Importing Media

After unzipping your video file, you should have a folder with a each of your
word videos in it. We'll copy all of those videos to the Anki media folder,
which is named `collections.media` where it stores things like videos, images,
and sounds that you can use in your flashcards.

1. Go to <a href="https://docs.ankiweb.net/files.html#file-locations">https://docs.ankiweb.net/files.html#file-locations</a> and find the folder that corresponds to your operating system (e.g,. macOS, Windows, or Linux).
2. Navigate to that folder.
3. In that folder, open the `collections.media` folder.
4. Copy all the word video files you downloaded into this folder. IMPORTANT: Do
   not rename these videos, or the Anki importable CSV created by the app will
   not work!

Your media is now accessible by Anki.

#### Step 3.2 (Expert/Manual): Importing Cards

1. Open Anki.
2. Open the deck you want to import the cards to.
3. Use the Anki menus to select "Import" (on a Mac, as of this writing, that's
   `File -> Import`.
4. Select the CSV you downloaded from the app after splitting your videos.
    1. Note that the first column of the CSV is the word, and the second column
       is the path to the video file for that word.
5. Select the card type to import to (`Basic (and reversed card)` is
   recommended).
6. Click `Import`.
7. You're done. Go study!


<a name="format-spec"></a>
## Format Specifications

<a name="csv-format-spec"></a>
### CSV Vocabulary List File Specification
CSV is an output format of many spreadsheet programs that's useful for storing
data that is naturally arranged in columns.

1. The [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) file MUST
   be as follows:
    1. The first column MUST be titled `word`
        1. The values in the `word` column can be anything and SHOULD correspond
           to the English translation of the sign
    2. The second column MUST be titled `start_time`
        1. The values in the `start_time` column must be float (decimal) numbers
           of the form `A.XYZ`. For example, `1.234`


#### Example of a Valid CSV Vocabulary List:
```
word,start_time
HELLO, 0.001
*wave*: hello or good bye, 2.604
GOOD+MORNING, 4.655
GOOD+AFTERNOON (formal), 7.152
GOOD+EVENING (formal), 9.500
GOOD+NIGHT, 12.655
```

Which, as a table, looks like:
<a name="rendered-vocabulary-csv"></a>

|word                     |start_time|
|-------------------------|----------|
|HELLO                    | 0.001    |
|*wave*: hello or good bye| 2.604    |
|GOOD+MORNING             | 4.655    |
|GOOD+AFTERNOON (formal)  | 7.152    |
|GOOD+EVENING (formal)    | 9.500    |
|GOOD+NIGHT               | 12.655   |


## FAQs

## Appendix

<a name="appendix-a"></a>
### Appendix A: Setting Up VLC for CSV Vocabulary List File Creation

To build the CSV Vocabulary list file, you must be able to precisely mark the
beginning of each word with its timestamp. While you can use any video playing
software that gives you this ability, the suggested method is using VLC, an
open-source video playing software, paired with an extension to give precise
timestamps. The following instructions will guide you through downloading that
software, installing the extension, and configuring that extension to help you
mark accurate timestamps.

1. Download VLC from: https://www.videolan.org/vlc/
1. Install VLC using the usual installation method for your system.
1. Download the `Time v3.2` VLC extension from: https://addons.videolan.org/p/1154032
    1. You can download the extension as a `.zip` from the `Files` tab.
1. Unzip the downloaded file.
1. Install the extension according to the instructions listed on the download
   page. They're somewhat hard to understand, but all the information is there.
   Alternatively (or in conjunction with the extension-provided install
   instructions), follow the macOS-specific procedure below and adapt it to your
   OS.
    1. Navigate to `/Applications/VLC.app/Contents/MacOS/share/lua` (note this
       path is also listed at the bottom of the download page, along with the
       paths for Windows and Linux).
        1. You can use Finder to get to this folder. Open Finder, then click on
           `Go -> Go to Folder` and enter the path above.
    1. You'll notice an `extensions` directory and an `intf` directory in this
       folder. You'll also notice that in the folder you unzipped, there's an
       `extensions` folder and an `intf` folder. Copy each file from its
       folder in the downloaded folder into its corresponding folder.
        1. The two files to copy should be named `time_ext.lua` and
           `time_intf.lua`
1. The extension is now installed.
1. Open VLC.
1. Open the Time extension configuration screen from the `VLC -> Extensions ->
   Time v3.2 (intf)` menu.
1. In the text input area in the configuration pop-up, enter the following
   pattern: `[E] / [D]`. This will lead to output overlayed on the video during
   playback like `01,155 / 01:01`.
    1. `[E]` is a special sequence that gets replaced with the current
       **E**lapsed time during video playback (i.e., the current point being
       viewed in the video).
    1. `[D]` is a special sequence that gets replaced with the **D**uration of the
       video.
    1. The `/` in between is just a literal character that will separate the two
       numbers during video playback to help you distinguish the two numbers.
    1. There are a variety of other special sequences you can use and patterns
       you can set. Feel free to explore, but we won't cover that here or
       support the usage of other patterns.
1. By default, the time markers appear in the `top-right` of the screen. You can
   configure that using the drop down menu, which is in the top right of the
   configuration pop-up.
1. Click `START!` (below the text input box)
1. If you open a video, you should now see a number that looks like `01,155 /
   01:01` overlayed on your screen.
1. As you play the video, you can pause it right before a word starts and note
   down the time to create the CSV Vocabulary List File.
    1. When creating the CSV Vocabulary List File, enter the start time using a
       `.` instead of a `,` (e.g., `1.155` instead of `1,155`) to separate the numbers. The number represents the
       elapsed time as `Seconds.Milliseconds`.
1. Congratulations! You're all ready to start creating CSV Vocabulary Lists.
