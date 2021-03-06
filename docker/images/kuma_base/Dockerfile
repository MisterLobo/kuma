FROM quay.io/mozmar/base:latest

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# disable this when preparing for Django upgrade
ENV PYTHONWARNINGS=ignore

WORKDIR /app
EXPOSE 8000

RUN apt-get update && \
    apt-get install -y --no-install-recommends python2.7 libpython2.7 python-dev \
    python-pip gettext build-essential \
    libtidy-0.99-0 libtidy-dev \
    libxml2-dev libxslt1.1 libxslt1-dev \
    libffi-dev \
    libjpeg-dev \
    libmagic-dev \
    libmysqlclient-dev \
    mysql-client  # Only for local dev.

# bug 1301116
RUN pip install setuptools==26.1.1

# Install the Node.js 6.9.2 LTS release.
ENV DEB_PKG=nodejs_6.9.2-1nodesource1~jessie1_amd64.deb
RUN curl -sLO https://deb.nodesource.com/node_6.x/pool/main/n/nodejs/${DEB_PKG}\
    && dpkg -i ${DEB_PKG} \
    && rm ${DEB_PKG} \
    && apt-get install -f

RUN update-alternatives --install /usr/bin/node node /usr/bin/nodejs 10

RUN npm install -g \
    fibers@1.0.15 \
    csslint@0.10.0 \
    jshint@2.7.0 \
    node-sass@4.3.0 \
    uglify-js@2.4.13 \
    clean-css@3.4.23 \
    stylelint@7.10.1
ENV PIPELINE_CSS_COMPRESSOR=kuma.core.pipeline.cleancss.CleanCSSCompressor \
    PIPELINE_CLEANCSS_BINARY=/usr/bin/cleancss \
    PIPELINE_JS_COMPRESSOR=pipeline.compressors.uglifyjs.UglifyJSCompressor \
    PIPELINE_UGLIFYJS_BINARY=/usr/bin/uglifyjs

COPY ./requirements /app/requirements
RUN pip install --no-cache-dir -r requirements/dev.txt

RUN useradd kuma
USER kuma

ENV WEB_CONCURRENCY=4
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout=120", "--worker-class=meinheld.gmeinheld.MeinheldWorker", "kuma.wsgi:application"]
