# trackday

## Setup

### MySQL
Connect to local MySQL
```
mysql -u root -h127.0.0.1 -p
```

Create Schema (172.17.0.1 is the IP used by clients connecting to the docker container. Use 172.0.0.1 if to connect local mysql instances)
```
CREATE USER 'trackday'@'172.17.0.1' IDENTIFIED WITH mysql_native_password BY 'trackday';
CREATE DATABASE trackday;
GRANT ALL ON trackday.* TO 'trackday'@'172.17.0.1'
```