#!/bin/bash -vx
PYTEST_ARGS="${@}"
if [ -z "$PYTEST_ARGS" ]; then
    PYTEST_ARGS="tests/functional -m \"not login\" -vv -sx"
fi
echo "ARGS=$PYTEST_ARGS"
BASE_URL=${BASE_URL:-https://developer.allizom.org}
NAME_SUFFIX=${NAME_SUFFIX:-kuma}
SELENIUM_TAG=${SELENIUM_TAG:-3.6.0}
BROWSERS=${BROWSERS:-chrome firefox}
SELENIUM_LOGS=${SELENIUM_LOGS:-0}

find . \( -name \*.pyc -o -name \*.pyo -o -name __pycache__ \) -prune -exec rm -rf {} +

(
  set -e
  docker build -t kuma-integration-tests:latest --pull=true -f docker/images/integration-tests/Dockerfile .
  docker run -d --name "selenium-hub-${NAME_SUFFIX}" "selenium/hub:${SELENIUM_TAG}"

  IFS=" "
  for browser in ${BROWSERS}; do
    docker run -d --name "selenium-node-${browser}-${NAME_SUFFIX}" --link selenium-hub-kuma:hub "selenium/node-${browser}:${SELENIUM_TAG}"
  done
  for browser in ${BROWSERS}; do
    cmd="pytest --driver Remote --capability browserName ${browser} --host hub --base-url=${BASE_URL} ${PYTEST_ARGS}"
    docker run --link "selenium-hub-${NAME_SUFFIX}:hub" kuma-integration-tests:latest sh -c "$cmd"
  done
)

if [[ "$SELENIUM_LOGS" != "0" ]]; then
  docker logs "selenium-hub-${NAME_SUFFIX}"
  for browser in ${BROWSERS}; do
    docker logs "selenium-node-${browser}-${NAME_SUFFIX}"
  done
fi

for browser in ${BROWSERS}; do
  docker stop "selenium-node-${browser}-${NAME_SUFFIX}"
  docker rm --volumes "selenium-node-${browser}-${NAME_SUFFIX}"
done
docker stop "selenium-hub-${NAME_SUFFIX}"
docker rm --volumes "selenium-hub-${NAME_SUFFIX}"
