apply:
	kubectl apply -f namespace.yaml && kubectl create configmap test-script --from-file=test.py --namespace alexey-testload && kubectl apply -f '*.yaml'

delete:
	kubectl delete -f namespace.yaml
