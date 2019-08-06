Name:      observatory-environment-server
Version:   4.0.5
Release:   0
Url:       https://github.com/warwick-one-metre/environmentd
Summary:   Environment daemon for the Warwick La Palma telescopes.
License:   GPL-3.0
Group:     Unspecified
BuildArch: noarch
Requires:  python36, python36-Pyro4, python36-jsonschema, python36-warwick-observatory-common,
Requires:  python36-warwick-observatory-environment, observatory-log-client, %{?systemd_requires}

%description
Part of the observatory software for the Warwick La Palma telescopes.

environmentd aggregates the status of the lower level enviroment daemons over a specified time interval
and exposes a single endpoint that can be queried to find all recent environment stats.

%build
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}/var/tmp/daemon_home/astropy
mkdir -p %{buildroot}%{_sysconfdir}/environmentd/

%{__install} %{_sourcedir}/environmentd %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/environmentd.service %{buildroot}%{_unitdir}
%{__install} %{_sourcedir}/sensors.json %{buildroot}%{_sysconfdir}/environmentd/

%post
%systemd_post environmentd.service

%preun
%systemd_preun environmentd.service

%postun
%systemd_postun_with_restart environmentd.service

%files
%defattr(0755,root,root,-)
%{_bindir}/environmentd
%defattr(-,root,root,-)
%{_unitdir}/environmentd.service
%{_sysconfdir}/environmentd/sensors.json
%dir /var/tmp/daemon_home/astropy

%changelog
