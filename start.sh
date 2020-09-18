docker-compose -f database-compose.yml --env-file covid_stats.env build
docker-compose -f database-compose.yml --env-file covid_stats.env up -d influxdb
docker-compose -f database-compose.yml  --env-file covid_stats.env up app
docker-compose -f plots-compose.yml  --env-file covid_stats.env up