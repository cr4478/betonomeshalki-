#!/bin/bash

# Запуск контейнеров с помощью docker-compose
echo "Starting containers using docker-compose..."
docker-compose up -d

until docker-compose exec db pg_isready -U user; do
  echo "Ожидание базы данных..."
  sleep 2
done


echo "Database is ready."

# Запуск миграций
echo "Running migrations..."
flask db upgrade

# Запуск Flask приложения
echo "Starting the Flask application..."
python app.py