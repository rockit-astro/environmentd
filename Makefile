RPMBUILD = rpmbuild --define "_topdir %(pwd)/build" \
        --define "_builddir %{_topdir}" \
        --define "_rpmdir %{_topdir}" \
        --define "_srcrpmdir %{_topdir}" \
        --define "_sourcedir %(pwd)"

all:
	mkdir -p build
	${RPMBUILD} -ba observatory-environment-server.spec
	${RPMBUILD} -ba observatory-environment-client.spec
	${RPMBUILD} -ba python36-warwick-observatory-environment.spec
	mv build/noarch/*.rpm .
	rm -rf build

