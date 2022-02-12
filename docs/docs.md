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

### Step 2: Using the ASL Flashcards App

### Step 3: Importing Flashcards to Anki

#### Step 3.1: Importing Media
#### Step 3.2: Importing Cards


## Format Specifications
<a name="format-spec"></a>

### CSV Vocabulary List File Specification
<a name="csv-format-spec"></a>
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

### Appendix A: Setting Up VLC for CSV Vocabulary List File Creation
<a name="appendix-a"></a>

