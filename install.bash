#!/bin/sh
source ./.env

# Safe Add PPA
wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
PG_PPA='deb http://apt.postgresql.org/pub/repos/apt/ '$(lsb_release -cs)'-pgdg main'
PG_PPA_FILE='/etc/apt/sources.list.d/pgdg.list'
grep -qF -- "$PG_PPA" "$PG_PPA_FILE" || echo "$PG_PPA" >> "$PG_PPA_FILE"

apt-get update --yes --quiet > /dev/null

# Uninstall older versions of postgres and install newer version
apt-get purge postgres* --yes --quiet > /dev/null
apt-get install postgresql postgresql-contrib --yes --quiet > /dev/null

#Creates the user and database automatically
sudo -u postgres psql postgres << EOF
 CREATE USER $DB_USER WITH PASSWORD '$DB_PASS' SUPERUSER;
 CREATE DATABASE $DB_NAME WITH OWNER $DB_USER;
EOF