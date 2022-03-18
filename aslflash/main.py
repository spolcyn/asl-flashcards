from io import BytesIO
import logging
from pathlib import Path

import pandas as pd
import streamlit as st
from pathvalidate import sanitize_filename
import yaml

from aslflash.utils import (
    get_vocab_timing_df,
    validate_word_timing_df,
    split_video,
    zip_dir,
    make_segment_string,
    rename_videos,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def render():
    if "logged_in" not in st.session_state:
        with open("logins.yml") as f:
            logins = yaml.safe_load(f)
        print(f"logins {logins}")

        username_in = st.empty()
        password_in = st.empty()
        username = username_in.text_input(label="Username")
        password = password_in.text_input(label="Password", type="password")

        try_login_in = st.empty()
        try_login = try_login_in.button(label="Login")
        if not try_login:
            return

        internal_username = username.lower()
        expected_password = logins["logins"].get(internal_username, None)
        if expected_password is None or expected_password != password:
            st.error("Login failed")
            logger.debug(
                f"Username {internal_username} not found (original: {username}"
            )
            return

        st.success(f"Login succeeded. Welcome, {username}.")
        st.session_state["logged_in"] = True
        st.session_state["username"] = internal_username

        # https://discuss.streamlit.io/t/delete-widgets/7596/6
        username_in.empty()
        password_in.empty()
        try_login_in.empty()

    # References:
    # https://superuser.com/questions/692714/how-to-split-videos-with-ffmpeg-and-segment-times-option
    # Time unit syntax: https://trac.ffmpeg.org/wiki/Seeking#Timeunitsyntax
    # Reset timestamps to avoid all videos black but the
    # first: https://trac.ffmpeg.org/ticket/142://trac.ffmpeg.org/ticket/1425

    st.title("ASL Flashcards")

    st.subheader("Vocab and Timing List Upload")

    choice = st.selectbox(
        "What do you want to do?", ["Make flashcards", "View documentation"]
    )

    if choice == "Make flashcards":
        render_app()
    elif choice == "View documentation":
        render_docs()
    else:
        assert False


def render_docs():
    doc_path = Path.cwd().parent / "docs" / "docs.md"
    with open(doc_path, mode="r") as doc_file:
        doc_body = doc_file.read()

    st.markdown(doc_body, unsafe_allow_html=True)


def render_app():
    vocab_timing_csv = st.file_uploader(
        "CSV file with Vocab and Timing info", type=["csv"]
    )
    segment_string = None
    vocab_timing_df = None
    if vocab_timing_csv:
        vocab_timing_data = BytesIO(vocab_timing_csv.getvalue())
        try:
            vocab_timing_df = get_vocab_timing_df(vocab_timing_data)
            validate_word_timing_df(vocab_timing_df)
        except ValueError as e:
            logger.exception(e)
            st.error(str(e))
            return

        st.dataframe(vocab_timing_df)

        segment_string = make_segment_string(vocab_timing_df)
        logger.debug("Segment string: %s", segment_string)

    st.subheader("Video Upload")

    finished_computation = False
    split_video_dir = None
    video_split_dependencies = [vocab_timing_df is not None, segment_string]
    if all(video_split_dependencies):
        video_file = st.file_uploader("Video with words signed")
        if video_file:
            video_data = video_file.getvalue()
            # TODO(spolcyn): Verify timestamps and video length are compatible
            # (i.e., largest time stamp < length of video)
            split_video_dir = split_video(video_data, segment_string)  # type: ignore
            vocab_timing_df["word"] = vocab_timing_df["word"].apply(sanitize_filename)
            rename_videos(split_video_dir, vocab_timing_df)
            finished_computation = True
            st.write("Done splitting video")

    else:
        st.write(
            "Video upload not available until vocab/timing CSV has been uploaded and validated"
        )

    st.subheader("Split Video Download")

    zip_videos_dependencies = [finished_computation, split_video_dir]
    if all(zip_videos_dependencies):
        # BOTH METHODS:
        # Create a zip file of the videos
        zip_output_path = zip_dir(split_video_dir)  # type: ignore

        # Create a CSV file to import to Anki
        VIDEO_OUTPUT_EXTENSION = "mp4"
        words = vocab_timing_df["word"]
        video_paths = [f"[sound:{word}.{VIDEO_OUTPUT_EXTENSION}]" for word in words]
        df_dict = {"word": words, "video_path": video_paths}
        anki_import_df = pd.DataFrame.from_dict(df_dict)
        anki_import_csv = bytes(
            anki_import_df.to_csv(line_terminator="\n", index=False), encoding="utf-8"
        )

        # LOCAL METHOD:
        # Read file into memory and make a download link for it
        LOCAL_MODE = True
        if LOCAL_MODE:
            with open(zip_output_path, "rb") as f:
                st.download_button(
                    label="Download ZIP of split videos",
                    data=f,
                    file_name="split_videos.zip",
                    mime="application/octet-stream",
                )

                st.download_button(
                    label="Download CSV to import to Anki",
                    data=anki_import_csv,
                    file_name="anki_import.csv",
                    mime="application/text",
                )
        else:
            # CLOUD METHOD:
            # Upload the zip file to S3 on a time-limited basis (say, 5-10min)
            # Get the link from where it was uploaded on S3
            # Use the URL link with the download part of the link to enable user to
            # download the file
            url = "test.com"
            href = f'<a href="{url}" download="split_videos.zip">Click to download split videos</a>'
            st.markdown(
                f"Download a zip of your files at {href}", unsafe_allow_html=True
            )
