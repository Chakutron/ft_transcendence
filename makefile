MAIN_PROJECT_NAME=main_project
ELK_PROJECT_NAME=elk_project

COMPOSE_FILE=docker-compose.yml
ELK_COMPOSE_FILE=docker-compose-elk.yml

COMPOSE=docker compose -f $(COMPOSE_FILE) -p $(MAIN_PROJECT_NAME)
ELK_COMPOSE=docker compose -f $(ELK_COMPOSE_FILE) -p $(ELK_PROJECT_NAME)

CONTAINER=$(c)

# Define a red color variable using ANSI escape code
GREEN=\033[32m
NC=\033[0m # No Color (reset)

up: down ssl-certs
	$(COMPOSE) build
	$(COMPOSE) up $(CONTAINER) -d || true

build:
	$(COMPOSE) build $(CONTAINER)

down:
	$(COMPOSE) down $(CONTAINER)

destroy:
	$(COMPOSE) down -v --rmi all
	docker image prune -f

ssl-certs:
	@if [ ! -f certs/ssl/private.key ] && [ ! -f certs/ssl/certificate.crt ]; then \
		echo "$(GREEN)SSL certificates not found, generating...$(NC)"; \
		mkdir -p certs/ssl; \
		openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
		-keyout certs/ssl/private.key -out certs/ssl/certificate.crt \
		-config config/ssl.conf; \
	else \
		echo "$(GREEN)SSL certificates already exist.$(NC)"; \
	fi

edit-hosts:    
	@echo "Checking and adding domains to /etc/hosts if they don't exist..."    
	@sudo sh -c 'echo "" >> /etc/hosts'
	@sudo sh -c 'grep -q "127.0.0.1 www.ft-transcendence.com" /etc/hosts || echo "127.0.0.1 www.ft-transcendence.com" >> /etc/hosts'
	@sudo sh -c 'grep -q "127.0.0.1 ft-transcendence.com" /etc/hosts || echo "127.0.0.1 ft-transcendence.com" >> /etc/hosts'

# Manage ELK stack
elk-up:
	$(ELK_COMPOSE) up -d || true

elk-down:
	$(ELK_COMPOSE) down 

elk-destroy:
	$(ELK_COMPOSE) down -v --rmi all
	docker image prune -f

kill-pid:
	sudo lsof -i :5432 | awk 'NR>1 {print $$2}' | xargs sudo kill -9 || true
	sudo lsof -i :5601 | awk 'NR>1 {print $$2}' | xargs sudo kill -9 || true
	sudo lsof -i :9200 | awk 'NR>1 {print $$2}' | xargs sudo kill -9 || true
	sudo lsof -i :8080 | awk 'NR>1 {print $$2}' | xargs sudo kill -9 || true
	sudo lsof -i :5044 | awk 'NR>1 {print $$2}' | xargs sudo kill -9 || true

db-shell:
	$(COMPOSE) exec db psql -U 42student players_db 

help:
	@echo "Usage:"
	@echo "  make build [c=service]        # Build images"
	@echo "  make up [c=service]           # Start containers in detached mode"
	@echo "  make start [c=service]        # Start existing containers"
	@echo "  make down [c=service]         # Stop and remove containers"
	@echo "  make destroy				   # Stop and remove containers and volumes"
	@echo "  make stop [c=service]         # Stop containers"
	@echo "  make logs [c=service]         # Tail logs of containers"
	@echo "  make ssl-certs                # create ssl certificate"
	@echo "  make edit-hosts			   # add host to /etc/hosts"

	@echo "  make help                     # Show this help"

.PHONY: up build start stop down destroy logs ps db-shell help

