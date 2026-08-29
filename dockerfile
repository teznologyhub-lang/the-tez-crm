FROM frappe/bench:latest

USER root
RUN apt-get update && apt-get install -y mariadb-client supervisor netcat-openbsd && rm -rf /var/lib/apt/lists/*

USER frappe
WORKDIR /home/frappe

# Initialize bench in non-interactive mode
RUN bench init --skip-redis-config-generation --frappe-branch version-15 frappe-bench

WORKDIR /home/frappe/frappe-bench

# Copy your local custom TezCRM app into bench
COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/crm

# Install app dependencies and build assets
RUN ./env/bin/pip install -e ./apps/crm && \
    bench build --app crm

EXPOSE 8000

COPY --chown=frappe:frappe docker/entrypoint.sh /home/frappe/entrypoint.sh
RUN chmod +x /home/frappe/entrypoint.sh

ENTRYPOINT ["/home/frappe/entrypoint.sh"]