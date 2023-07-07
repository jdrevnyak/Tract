# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11

# Set the working directory in the container to /app
WORKDIR /user/src/app

COPY './requirements.txt' .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 5000 available to the world outside this container
COPY . .

ENTRYPOINT [ "python", "app.py" ]