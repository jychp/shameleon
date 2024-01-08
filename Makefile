lint: python-lint golang-lint

python-lint:
	pre-commit run --all-files --show-diff-on-failure

golang-lint:
	cd backdoor_src && ~/go/bin/golangci-lint run
