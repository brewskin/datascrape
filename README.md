# datascrape

## Setup

This setup is run on a Windows 10 PC using Git Bash.

### Create your virtual environment

Docs for [reference](https://docs.python.org/3/library/venv.html).

First create the virtual environment directory.

```sh
python -m venv venv
```

Then source the activation script.

```sh
source venv/Scripts/activate
```

### Install Dependencies

Install the project requirements.txt

```sh
pip install -r requirements.txt
```

### Docker

Install Docker [here](https://docs.docker.com/desktop/install/windows-install/).

After installation go into the Settings -> General -> Enable Docker Compose V2. Check that box and apply the changes.

## Running 

Use docker-compose to start the postgres table. 
Docker should automatically pull the postgres docker image if it does not exist.

```sh
docker compose up -d
```

Use your preferred database IDE and run the [migrations](/migrations/).

Finally, run the Flask app.

```sh
python assistant.py
```

You should be able to navigate to the [locally](http://127.0.0.1:5000/) running app. 
Give it a link and it should insert some stuff into the database.

