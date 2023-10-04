# ASL Flashcard Builder

## Installation

### Docker

1. Install Docker: https://docs.docker.com/engine/install/
2. Run `docker compose up app` to build and run the container
3. Open the Streamlit app by clicking on the link in the container logs
   (typically, `localhost:9000`)

### Python
1. Install dependencies: `pip install -r requirements.txt`
2. Add module to Python path: `python setup.py develop`
3. Start streamlit: `python -m streamlit run aslflash/app.py`
