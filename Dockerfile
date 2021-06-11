### --------------------------------------------------------------------
### Docker Build Arguments
### Available only during Docker build - `docker build --build-arg ...`
### --------------------------------------------------------------------
ARG ALPINE_VERSION="3.13"
ARG PYTHON_VERSION="3.9.1"
ARG APP_NAME="frigga"
ARG APP_PYTHON_USERBASE="/frigga"
ARG APP_USER_NAME="appuser"
ARG APP_USER_ID="1000"
ARG APP_GROUP_NAME="appgroup"
ARG APP_GROUP_ID="1000"
### --------------------------------------------------------------------


### --------------------------------------------------------------------
### Build Stage
### --------------------------------------------------------------------
FROM python:"$PYTHON_VERSION"-alpine"${ALPINE_VERSION}" as build

ARG APP_PYTHON_USERBASE

# Define env vars
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUSERBASE="$APP_PYTHON_USERBASE" \
    PATH="${APP_PYTHON_USERBASE}/bin:${PATH}"

# Upgrade pip and then install build tools
RUN pip install --upgrade pip && \
    pip install --upgrade wheel setuptools wheel check-wheel-contents

# Define workdir
WORKDIR "$APP_PYTHON_USERBASE"

# Copy and install requirements - better caching
COPY requirements.txt .
RUN pip install -r "requirements.txt" --no-warn-script-location

# Copy the application from Docker build context to WORKDIR
COPY . .

ARG GITHUB_SHA
ENV GITHUB_SHA=${GITHUB_SHA}

# Build the application, validate wheel contents and install the application
RUN \
    python setup.py bdist_wheel && \
    find dist/ -type f -name *.whl \
    -exec check-wheel-contents {} \; \
    -exec pip install --prefix="/dist" -r "requirements.txt" --ignore-installed --no-warn-script-location {} \;

WORKDIR /dist/

# For debugging the Build Stage
CMD ["bash"]
### --------------------------------------------------------------------


### --------------------------------------------------------------------
### App Stage
### --------------------------------------------------------------------
FROM python:"$PYTHON_VERSION"-alpine"${ALPINE_VERSION}" as app

# Fetch values from ARGs that were declared at the top of this file
ARG APP_NAME
ARG APP_PYTHON_USERBASE
ARG APP_USER_ID
ARG APP_USER_NAME
ARG APP_GROUP_ID
ARG APP_GROUP_NAME

# Define env vars
ENV HOME="$APP_PYTHON_USERBASE" \
    PYTHONUSERBASE="$APP_PYTHON_USERBASE" \
    APP_NAME="$APP_NAME" \
    PYTHONUNBUFFERED=0
ENV PATH="${PYTHONUSERBASE}/bin:${PATH}"

# Define workdir
WORKDIR "$PYTHONUSERBASE"

# Run as a non-root user
RUN \
    addgroup -g "${APP_GROUP_ID}" "${APP_GROUP_NAME}" && \
    adduser -H -D -u "$APP_USER_ID" -G "$APP_GROUP_NAME" "$APP_USER_NAME" && \
    chown -R "$APP_USER_ID":"$APP_GROUP_ID" "$PYTHONUSERBASE"
USER "$APP_USER_NAME"

# Copy artifacts from Build Stage
COPY --from=build --chown="$APP_USER_NAME":"$APP_GROUP_ID" /dist/ "$PYTHONUSERBASE"/

# The container runs the application, or any other supplied command, such as "bash" or "echo hello"
# CMD python -m ${APP_NAME}

# Use ENTRYPOINT instead CMD to force the container to start the application
ENTRYPOINT ["frigga"]
### --------------------------------------------------------------------
