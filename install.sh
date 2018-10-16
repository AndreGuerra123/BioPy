source ./.env

# Safe Add PPA
sudo wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
PG_PPA='deb http://apt.postgresql.org/pub/repos/apt/ '$(lsb_release -cs)'-pgdg main'
PG_PPA_FILE='/etc/apt/sources.list.d/pgdg.list'
sudo grep -qF -- "$PG_PPA" "$PG_PPA_FILE" || sudo echo "$PG_PPA" >> "$PG_PPA_FILE"

sudo apt-get update --yes --quiet > /dev/null

# Uninstall older versions of postgres and install newer version
sudo apt-get purge postgres* --yes --quiet > /dev/null
sudo apt-get install postgresql postgresql-contrib --yes --quiet > /dev/null

#Creates the user and database automatically
sudo -u postgres psql postgres << EOF
 CREATE USER $USER WITH PASSWORD '$PASS' SUPERUSER;
 CREATE DATABASE $DB_NAME WITH OWNER $USER;
EOF