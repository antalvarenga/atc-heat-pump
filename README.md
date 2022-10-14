# Aveiro Tech City - Heat Pump Optimization

Heat pump optimization algorithm based on the challenge for the Aveiro Tech City Hackathon.


![alt text](https://github.com/antalvarenga/atc-heat-pump/blob/master/Architecture_Diagram.png?raw=true)

# Setup and Run

For frontend:

- Install Node.js using https://github.com/nvm-sh/nvm

- To install frontend requirements run: ```npm install```

- To start frontend run: ```npm run start```

For backend:

- Install python 3.9 using https://www.python.org/downloads/

- Install poetry (dependency manager):

    ```pip install poetry```

- Install dependencies: 

    ```cd Optimization/```

    ```poetry install```

- Run backend:

    ```poetry run flask --app main run --port=5010```

- Run APIs:

    ```cd ExternalAPI/```

    ```poetry run flask --app api_electricity run --port=5001```

    ```poetry run flask --app api_temperature_Braganca run --port=5002```

- Run continuous thermal model:

    ```poetry run python thermal_model.py```


# Repository Structure

- fe - Frontend code

- Optimization - Backend code:

    - ExternalAPI: Temperature and Price APIs

    - main.py - Backend API

    - hackathon.py - Base model optimization code

    - thermal_model.py - Continuous model optimization code
