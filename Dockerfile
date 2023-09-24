# Start from the latest Debian image
FROM debian:11

# Install python3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy the current directory contents into the container at /app
ADD . /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Put the module in the path
RUN python3 setup.py develop

WORKDIR /app/aslflash

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py"]
