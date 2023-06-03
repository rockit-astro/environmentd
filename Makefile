RPMBUILD = rpmbuild --define "_topdir %(pwd)/build" \
        --define "_builddir %{_topdir}" \
        --define "_rpmdir %{_topdir}" \
        --define "_srcrpmdir %{_topdir}" \
        --define "_sourcedir %(pwd)"

all:
	mkdir -p build
	${RPMBUILD} -ba observatory-environment-server.spec
	${RPMBUILD} -ba observatory-environment-client.spec
	${RPMBUILD} -ba python3-warwick-observatory-environment.spec
	mv build/noarch/*.rpm .
	rm -rf build

install:
	@python3 setup.py install
	@cp environmentd environment /bin/
	@cp environmentd@.service /usr/lib/systemd/system/
	@cp completion/environment /etc/bash_completion.d/
	@install -d /etc/environmentd
	@echo ""
	@echo "Installed server, client, and service files."
	@echo "Now copy the relevant json config files to /etc/environmentd/"
