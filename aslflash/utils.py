import shutil
import os
import logging
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile, mkdtemp

import pandas as pd
import streamlit as st
import genanki

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

card_style = """
.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: white;
}
"""

# TODO(spolcyn): Make a more robust way to generate the model_id, given that it
# may overlap with existing user decks
asl_model = genanki.Model(
    model_id=1486321964,
    name="Anki ASL",
    fields=[
        {"name": "Word"},
        {"name": "Video"},
        {"name": "Notes"},
    ],
    templates=[
        {
            "name": "Word to ASL",
            "qfmt": "Word: {{Word}}",
            "afmt": "{{FrontSide}}<hr id=answer>{{Video}}<br><br>Notes: {{Notes}}",
        },
        {
            "name": "ASL to Word",
            "qfmt": "ASL: {{Video}}",
            "afmt": "{{FrontSide}}<hr id=answer>{{Word}}<br><br>Notes: {{Notes}}",
        },
    ],
    css=card_style,
)

# TODO(spolcyn): Make a more robust way to generate the deck_id, given that it
# may overlap with existing user decks
def get_asl_anki_deck() -> genanki.Deck:
    return genanki.Deck(deck_id=1374105886, name="ASL Anki")


def get_vocab_timing_df(csv_source) -> pd.DataFrame:
    dtype_dict = {
        "word": "string",
        "start_time": "float64",
    }

    try:
        return pd.read_csv(csv_source, dtype=dtype_dict)
    except ValueError as exc:
        raise ValueError(
            "Column values were the wrong types. "
            "Review the docs to ensure your CSV coforms to the format specification."
        )


def make_segment_string(vocab_timing_df: pd.DataFrame) -> str:
    """
    Make the string that passed to ffmpeg that has the times dividing segments.

    Args:
        pd.DataFrame vocab_timing_df: Dataframe with vocab words and where they
            start in the video columns.

    Returns:
        str: String with the comma-separate segment markers.
            Example: "1.532,2.730,3.435"
    """
    return ",".join([str(time) for time in vocab_timing_df["start_time"]])


@st.cache
def rename_videos(split_video_dir: str, word_timing_df: pd.DataFrame) -> None:
    # Get absolute file paths of the videos in the dir
    # Parse filename to get the index -- just split on the '.' for the extension
    # Use the index to access the correct row in the DF
    # Rename the file to be `word.ext`
    logger.info(f"Renaming videos in directory {split_video_dir}")
    filenames = os.listdir(split_video_dir)
    logger.info(f"Filenames {filenames}")

    for filename in filenames:
        segment_number, extension = filename.split(".")
        segment_number = int(segment_number)
        logger.info("Renaming video %s", segment_number)

        if segment_number == 0:
            os.remove(os.path.join(split_video_dir, filename))
            continue

        index = segment_number - 1
        word = word_timing_df["word"].iloc[index]
        os.rename(
            os.path.join(split_video_dir, filename),
            os.path.join(split_video_dir, f"{word}.{extension}"),
        )


@st.cache
def split_video(video_data: bytes, segment_string: str) -> str:
    """
    Splits a video into segments

    Args:
        bytes video_file: Uploaded video file
        str segment_string: String with comma-separated timestamps to
            split on

    Returns:
        str: Path to directory where split videos are
    """
    ffmpeg_command = " ".join(
        [
            "ffmpeg",
            "-i {video_path}",
            "-f segment",
            "-segment_times {segment_string}",
            "-force_key_frames {segment_string}",
            "-c:v libx264",
            "-map 0",
            "-c:a copy",
            "-reset_timestamps 1",
            "-segment_time_delta 0.021",  # 1 / (2 * 24)
            "{output_file_format}",
        ]
    )

    with NamedTemporaryFile(suffix=".mov", mode="wb") as f:
        f.write(video_data)
        f.flush()
        logger.debug(f"Named temporary file is at {f.name}")

        # https://stackoverflow.com/questions/10541760/can-i-set-the-umask-for-tempfile-namedtemporaryfile-in-python
        os.chmod(f.name, 0o644)

        # Setup the tempdir for output
        split_video_dir = mkdtemp()
        os.chmod(
            split_video_dir, 0o744
        )  # ensure execute and write ermissions are set on the directory
        logger.info("Output will be at: %s", split_video_dir)

        # Configure the command
        output_file_format = f"{split_video_dir}/%d.mp4"
        command = ffmpeg_command.format(
            video_path=f.name,
            segment_string=segment_string,
            output_file_format=output_file_format,
        )
        logger.info("ffmpeg command to run:\n%s", command)
        command_out = subprocess.run(command, capture_output=True, shell=True)
        logger.info("Command out:\n%s", command_out)

        # Remove the initial segment before the first word
        # os.remove(os.path.join(split_video_dir, "0.mov"))
        logger.info("Not removing")

    return split_video_dir


def validate_word_timing_df(csv_df: pd.DataFrame) -> bool:
    required_columns = ["word", "start_time"]
    if not all([column in csv_df.columns for column in required_columns]):
        raise ValueError(
            f"Expected {required_columns} as columns (got {list(csv_df.columns)})"
        )

    column_to_dtype = {
        "word": "string",
        "start_time": "float64",
    }
    for column, dtype in column_to_dtype.items():
        if not csv_df.dtypes[column] == dtype:
            raise ValueError(
                f"Expected column {column} to be dtype {dtype} (got {csv_df.dtypes[column]})"
            )

    deduplicated_words = set(csv_df["word"])
    if len(deduplicated_words) != len(csv_df["word"]):
        duplicated_words = []
        temp_set = set()
        for word in csv_df["word"]:
            len_before = len(temp_set)
            temp_set.add(word)
            if len(temp_set) == len_before:
                duplicated_words.append(word)

        duplicated_words_str = ", ".join(duplicated_words)

        raise ValueError(
            f"Got {duplicated_words_str} multiple times, all words must be unique"
        )

    return True


def zip_dir(source_dir: str) -> str:
    """
    Zips the provided directory and returns a path to the zip file

    Args:
        str source_dir: Directory to archive

    Returns:
        str: Path to the created zip file
    """
    zip_output_dir = mkdtemp()
    logger.debug(f"Zipping directory {source_dir}")

    zip_output_path = shutil.make_archive(
        os.path.join(zip_output_dir, "split_videos"), "zip", source_dir
    )
    logger.info("Created ZIP output at: %s", zip_output_path)

    return zip_output_path


def build_apkg_from_df(anki_import_df: pd.DataFrame, split_video_dir: str):
    notes = [
        genanki.Note(model=asl_model, fields=[video, word, ""], tags=tags)
        for (video, word, tags) in zip(
            anki_import_df["word"], anki_import_df["video_path"], anki_import_df["tags"]
        )
    ]

    deck = get_asl_anki_deck()
    for note in notes:
        deck.add_note(note)

    video_files = [f for f in Path(split_video_dir).iterdir() if f.is_file()]
    logger.debug(f"Adding video files to apkg: {video_files}")

    package = genanki.Package(deck)
    package.media_files = video_files

    return package
