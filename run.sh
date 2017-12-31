#!/bin/bash

ALLECENA_PATH="`dirname \"$0\"`"

echo "Script paths: $ALLECENA_PATH"

mkdir -p $ALLECENA_PATH/logs

source $ALLECENA_PATH/env/bin/activate

# konsole --new-tab -e "python $ALLECENA_PATH/app/manage.py celeryd --verbosity=2 --loglevel=DEBUG -c 8"
# konsole --new-tab -e "python $ALLECENA_PATH/app/manage.py celerybeat --verbosity=2 --loglevel=DEBUG"
# konsole --new-tab -e "python $ALLECENA_PATH/app/manage.py runserver 8000"

python $ALLECENA_PATH/app/manage.py celeryd --verbosity=2 --loglevel=DEBUG -c 8 > $ALLECENA_PATH/logs/celeryd.system.log 2>&1 &
python $ALLECENA_PATH/app/manage.py celerybeat --verbosity=2 --loglevel=DEBUG > $ALLECENA_PATH/logs/celerybeat.system.log 2>&1 &
python $ALLECENA_PATH/app/manage.py runserver 8000 > $ALLECENA_PATH/logs/server.system.log 2>&1 &

echo "Done!"
