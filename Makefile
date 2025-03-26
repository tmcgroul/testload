apply-stream:
	kubectl apply -f namespace.yaml && kubectl create configmap test-script --from-file=stream/test.py --namespace alexey-testload && kubectl apply -f 'stream/*.yaml'

apply-rpc:
	kubectl apply -f namespace.yaml && kubectl apply -f 'rpc/*.yaml'

delete:
	kubectl delete -f namespace.yaml
