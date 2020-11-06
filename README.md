# Welcome to Talaria!

**Talaria** is a web based tool that is used alongside [**Strava**](https://www.strava.com/) to help create, plan, execute and monitor any and all running goals you may have, from running your first ever 5km to getting ready for your next marathon!

# Files

The **frontend** folder contains all the code relevant to the Reactjs frontend for the app

Similarly, the **api** folder holds all the code to handle the python flask backend

# Prerequisites

Before being able to run the project, there are a few things we must set up and install.

**Frontend:**
1. The frontend requires 2 packages to be installed:
	-   [Node.js](https://nodejs.org/): The JavaScript runtime that you will use to run your frontend project.
	-    [Yarn](https://yarnpkg.com/): A package and project manager for Node.js applications.
2. `cd frontend` and run the command `npm install`

**API:**
 1. The api requires 1 package to be installed:
	 - [Python](https://python.org/): A recent Python 3 interpreter to run 	the Flask backend on.
2.  `cd api` and create a virtualenv `py -m venv venv`
3.  Activate the venv with `venv\Scripts\activate`
4. Install the required packages with the command `pip install -r requirements.txt`
5.  Run the command `cp .flaskenv.local .flaskenv` to create your own env. Fill in the blank variables with your own details. To get your strava credentials you should follow this [video](https://www.youtube.com/watch?v=sgscChKfGyg&t=18s)

# Running the app

You will need two terminal tabs open, with one being in the `frontend` directory and the other in the `api` directory

 1. In the frontend tab, run the command ```yarn start``` to run the 		react frontend
 2. In the api tab run the command ```flask run``` to run the flask backend

Finally, direct your browser to ```localhost:3000``` and you should be good to go!
