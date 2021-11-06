.PHONY: start stop restart

help:
	@echo  ''
	@echo  '  start     - Starts all of the deployments needed for slinky'
	@echo  '  stop      - Deletes all of the deployments'
	@echo  '  restart   - Deletes all ofthe deployments and starts all of them'
	@echo  ''
	@echo  ''

start:
	kubectl apply -f deployment/redis-deployment.yaml
	kubectl apply -f deployment/virtuoso-deployment.yaml
	kubectl rollout status deploy/redis
	kubectl rollout status deploy/virtuoso
	kubectl apply -f deployment/worker-default-deployment.yaml
	kubectl apply -f deployment/worker-dataset-deployment.yaml
	kubectl apply -f deployment/scheduler-deployment.yaml
	kubectl rollout status deploy/worker-default
	kubectl rollout status deploy/worker-dataset
	kubectl rollout status deploy/scheduler
	echo 'Successfully deployed the deployments'

stop:
	kubectl delete deployment scheduler redis virtuoso worker-dataset worker-default

restart: stop start