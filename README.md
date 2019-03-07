# trackday

## Setup

### Postgres
* Connect to local Postgres
```
psql -h localhost -d trackday -U trackday
```
* Create Schema
```
psql -h localhost -U postgres
CREATE USER trackday;
ALTER USER trackday WITH PASSWORD 'trackday';
CREATE DATABASE trackday;
GRANT ALL PRIVILEGES ON DATABASE trackday to trackday;
```