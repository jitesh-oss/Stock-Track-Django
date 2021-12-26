
# Stock Track

Add, Edit and View Equity Stocks from NSE and BSE to monitor their current position with respect to latest price.


## Version 1

- Live NSE/BSE search
- Auto fetch prices
- Range bar to view current status of shares
- Indication of status when certain point of interest is reached


## Installation

Install stock-track with Docker :

#### Requirements
- git
- Docker

Once the requirements are met, make a new folder and open terminal/cmd in that folder and run the following commands:

```bash
  git clone <repo> .
```
Rename .env.sample to .env

```bash
  docker-compose up --build
```
Once the packages are downloaded and server is up, the app can be accessed by navigating to http://127.0.0.1:85

To retain data in database, make sure you don't delete the container.

### To stop the containers:
Make sure you're in the root directory of the project.

```bash
  docker stop stock_track
  docker stop nginx
```

### To start the containers:
Make sure you're in the root directory of the project.
```bash
  docker start stock_track
  docker start nginx
```