from io import BytesIO
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
import streamlit as st
from pathvalidate import sanitize_filename
from streamlit_tags import st_tags

from aslflash.utils import (
    build_apkg_from_df,
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
    # References:
    # https://superuser.com/questions/692714/how-to-split-videos-with-ffmpeg-and-segment-times-option
    # Time unit syntax: https://trac.ffmpeg.org/wiki/Seeking#Timeunitsyntax
    # Reset timestamps to avoid all videos black but the
    # first: https://trac.ffmpeg.org/ticket/142://trac.ffmpeg.org/ticket/1425

    st.title("ASL Flashcards")

    st.header("Vocab and Timing List Upload")

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
    doc_path = Path(__file__).parent.parent / "docs" / "docs.md"
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

    st.header("Video Upload")

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

    st.header("Split Video Download")

    words = None
    video_paths = None
    zip_videos_dependencies = [finished_computation, split_video_dir]
    if all(zip_videos_dependencies):
        zip_output_path = zip_dir(split_video_dir)  # type: ignore

        # Create a CSV file to import to Anki
        VIDEO_OUTPUT_EXTENSION = "mp4"
        words = vocab_timing_df["word"]
        video_paths = [f"[sound:{word}.{VIDEO_OUTPUT_EXTENSION}]" for word in words]

    anki_import_dependencies = [words is not None, video_paths is not None]
    if all(anki_import_dependencies):
        tags = st_tags(
            label="Anki tags for flashcards",
            text="Press enter after each tag",
            suggestions=["asl-lesson1"],
            maxtags=-1,
        )

        done_with_tags = st.button("Finish adding tags and generate flashcard deck")
        if not done_with_tags:
            return

        card_tags = [tags for _ in range(len(words))]
        df_dict = {"word": words, "video_path": video_paths, "tags": card_tags}
        anki_import_df = pd.DataFrame.from_dict(df_dict)
        anki_import_csv = bytes(
            anki_import_df.to_csv(line_terminator="\n", header=False, index=False),
            encoding="utf-8",
        )

        # Create APKG to import to Anki
        deck_apkg = build_apkg_from_df(anki_import_df, split_video_dir)
        with NamedTemporaryFile(delete=False, suffix=".apkg") as deck_file:
            deck_apkg.write_to_file(deck_file)

        st.subheader("Recommended Download Mode")
        with open(deck_file.name, "rb") as deck_apkg:
            st.download_button(
                label="Download Anki Package to import to Anki",
                data=deck_apkg,
                file_name="asl_anki.apkg",
                mime="application/octet-stream",
            )

        st.subheader("Expert/Manual Download Mode")
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
