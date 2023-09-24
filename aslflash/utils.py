import shutil
import os
import logging
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile, mkdtemp
from typing import Iterable

import pandas as pd
import streamlit as st
import genanki

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

card_style: str = """
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


def get_vocab_timing_df(csv_source: str) -> pd.DataFrame:
    """Get the vocab/timing data with the correct types"""
    column_to_type: dict[str, str] = {
        "word": "string",
        "start_time": "float64",
    }

    try:
        return pd.read_csv(csv_source, dtype=column_to_type)
    except ValueError as exc:
        raise ValueError(
            "Column values were the wrong types. "
            "Review the docs to ensure your CSV conforms to the format specification."
        ) from exc


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
def rename_videos(split_video_dir: str, words: Iterable[str]) -> None:
    """
    Renames the split clips according to the vocabulary words they correspond to

    Args:
        split_video_dir: Directory containing the clips, expected to be named
            "<n>.ext" for n in [0, # vocab words]. Clip 0 is discarded.
        words: Iterable that contains the words in the order they appear in the
            video.

    """
    logger.info(f"Renaming videos in directory {split_video_dir}")
    filenames = sorted(os.listdir(split_video_dir))
    logger.info(f"Filenames {filenames}")

    words = iter(words)
    for filename in filenames:
        segment_number, extension = filename.split(".")
        logger.info("Renaming video %s", segment_number)

        if segment_number == "0":
            os.remove(os.path.join(split_video_dir, filename))
            continue

        word: str = next(words)
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

    return split_video_dir


def validate_word_timing_data(word_timing_data: pd.DataFrame) -> bool:
    """Validates a vocab and timing data input. Raises `ValueError` if any
    issues are found in the input"""
    required_columns: list[str] = ["word", "start_time"]
    if not all([column in word_timing_data.columns for column in required_columns]):
        raise ValueError(
            f"Expected {required_columns} as columns (got {list(word_timing_data.columns)})"
        )

    column_to_dtype: dict[str, str] = {
        "word": "string",
        "start_time": "float64",
    }
    for column, dtype in column_to_dtype.items():
        if not word_timing_data.dtypes[column] == dtype:
            raise ValueError(
                f"Expected column {column} to be dtype {dtype} (got {word_timing_data.dtypes[column]})"
            )

    duplicate_mask: pd.Series = word_timing_data.duplicated(subset=["word"])
    if any(duplicate_mask):
        duplicated_words: str = ", ".join(word_timing_data["word"][duplicate_mask])
        raise ValueError(
            f"Got {duplicated_words} multiple times, all words must be unique"
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
    zip_output_dir: str = mkdtemp()
    logger.debug(f"Zipping directory {source_dir}")

    zip_output_path: str = shutil.make_archive(
        os.path.join(zip_output_dir, "split_videos"), "zip", source_dir
    )
    logger.info("Created ZIP output at: %s", zip_output_path)

    return zip_output_path


def build_apkg_from_df(
    anki_import_df: pd.DataFrame, split_video_dir: str
) -> genanki.Package:
    """
    Builds an Anki `.apkg` file from pipeline output

    Args:
        anki_import_df: CSV that would be suitable for importing to Anki,
            including paths to the videos attached to each flashcard
        split_video_dir: Path to directory holding media that would be imported
            alongside the CSV
    """
    notes: list[genanki.Note] = [
        genanki.Note(model=asl_model, fields=[video, word, ""], tags=tags)
        for (video, word, tags) in zip(
            anki_import_df["word"], anki_import_df["video_path"], anki_import_df["tags"]
        )
    ]

    deck: genanki.Deck = get_asl_anki_deck()
    for note in notes:
        deck.add_note(note)

    video_files: list[Path] = [
        f for f in Path(split_video_dir).iterdir() if f.is_file()
    ]
    logger.debug(f"Adding video files to apkg: {video_files}")

    package: genanki.Package = genanki.Package(deck)
    package.media_files = video_files

    return package
