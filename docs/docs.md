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

1. Open your video in VLC.

### Step 2: Using the ASL Flashcards App

### Step 3: Importing Flashcards to Anki

#### Step 3.1: Importing Media
#### Step 3.2: Importing Cards


## Format Specifications
<a name="format-spec"></a>

### CSV Vocabulary List File Specification
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

