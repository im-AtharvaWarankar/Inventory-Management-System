#!/bin/bash
modes="  start-dev\n  stop-dev\n  start-prod\n  stop-prod\n  interactive-dev\n  interactive-prod\n  check-syntax\n  start-deploy\n  migrate\n  sync-vault\n  check-setup\n  db-backup"
mode=$1
project_name="bynry"

if [ "$project_name" == "*****" ]; then
    echo "Please Update the Project Name in run.sh"
    exit 0;
fi

if [ "$mode" == "" ]; then
    echo -e $"Invalid mode \nPlease enter one of the following mode:\n${modes}"
elif [ "$mode" == "start-dev" ]; then
    if [ ! -f src/vault.py ]; then
        echo -e "vault file not found! \nPlease download the it.\nRefer the README for more information."
        exit 1;
    fi
    docker-compose -p ${project_name}-dev -f docker-compose-dev.yml build
    docker-compose -p ${project_name}-dev -f docker-compose-dev.yml up -d
elif [ "$mode" == "stop-dev" ]; then
    docker-compose -p ${project_name}-dev -f docker-compose-dev.yml down
elif [ "$mode" == "interactive-dev" ]; then
    docker exec -it --user root ${project_name}-backend bash
elif [ "$mode" == "start-prod" ]; then
    if [ ! -f src/vault.py ]; then
        echo -e "vault file not found! \nPlease download the it.\nRefer the README for more information."
        exit 1;
    fi
    docker-compose -p ${project_name}-prod build
    docker-compose -p ${project_name}-prod up -d
elif [ "$mode" == "stop-prod" ]; then
    docker-compose -p ${project_name}-prod down
elif [ "$mode" == "interactive-prod" ]; then
    docker exec -it --user root ${project_name}-backend bash
elif [ "$mode" == "check-syntax" ]; then
    docker exec -it --user root ${project_name}-backend flake8 .
elif [ "$mode" == "sync-vault" ]; then
    docker exec -it --user root ${project_name}-backend python manage.py sync-vault
elif [ "$mode" == "check-setup" ]; then
    docker exec -it --user root ${project_name}-backend python manage.py check-setup
elif [ "$mode" == "db-backup" ]; then
    docker exec -it --user root ${project_name}-backend python manage.py db-backup
else
    echo -e $"Invalid mode \nPlease enter one of the following mode:\n${modes}"
fi