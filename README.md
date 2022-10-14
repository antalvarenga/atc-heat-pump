# Aveiro Tech City - Heat Pump Optimization

Heat pump optimization algorithm based on the challenge for the Aveiro Tech City Hackathon.

# Setup

For frontend:

- Install Node.js using https://github.com/nvm-sh/nvm

- To install frontend requirements run: ```npm install```

- To start frontend run: ```npm run start```

For backend:

- Install python 3.9 using https://www.python.org/downloads/

- Install poetry (dependency manager): ```pip install poetry```

- Install dependencies: ```poetry install```

- Run backend: ```poetry run flask --app main run --port=5010```

- Run APIs:

    ```cd Optimization/ExternalAPI/```

    ```poetry run flask --app api_electricity run --port=5001```

    ```poetry run flask --app api_temperature_Braganca run --port=5002```

