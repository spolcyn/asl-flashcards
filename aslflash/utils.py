import shutil
import os
import logging
import subprocess
from tempfile import NamedTemporaryFile, mkdtemp

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


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
    ffmpeg_command = (
        "ffmpeg -i {video_path} -f segment -segment_times {segment_string} "
        '-c:v copy -map 0 -c:a copy -reset_timestamps 1 "{output_file_format}"'
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
        output_file_format = f"{split_video_dir}/word%d.mov"
        command = ffmpeg_command.format(
            video_path=f.name,
            segment_string=segment_string,
            output_file_format=output_file_format,
        )
        logger.info("ffmpeg command to run:\n%s", command)
        command_out = subprocess.run(command, capture_output=True, shell=True)
        logger.debug("Command out:\n%s", command_out)

    return split_video_dir


def validate_timing_csv(csv_df: pd.DataFrame) -> bool:
    return all(
        [
            "word" in csv_df.columns,  # type: ignore
            "start_time" in csv_df.columns,  # type: ignore
            csv_df.dtypes["word"] == "string",
            csv_df.dtypes["start_time"] == "float64",
        ]
    )


def zip_dir(source_dir: str) -> str:
    """
    Zips the provided directory and returns a path to the zip file

    Args:
        str source_dir: Directory to archive

    Returns:
        str: Path to the created zip file
    """
    zip_output_dir = mkdtemp()
    logger.debug("Creating zip outout...")

    zip_output_path = shutil.make_archive(
        os.path.join(zip_output_dir, "split_videos"), "zip", source_dir
    )
    logger.info("Created ZIP output at: %s", zip_output_path)

    return zip_output_path
