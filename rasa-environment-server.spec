Name:      rasa-environment-server
Version:   3.1.2
Release:   0
Url:       https://github.com/warwick-one-metre/environmentd
Summary:   Environment daemon for the RASA prototype telescope.
License:   GPL-3.0
Group:     Unspecified
BuildArch: noarch
Requires:  python34, python34-Pyro4, python34-pyephem, python34-warwick-observatory-common,
Requires:  python34-warwick-observatory-environment, observatory-log-client, %{?systemd_requires}

%description
Part of the observatory software for the RASA prototype telescope.

environmentd aggregates the status of the lower level enviroment daemons over a specified time interval and determines whether it is safe to observe.

%build
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}/var/tmp/daemon_home/astropy

%{__install} %{_sourcedir}/environmentd %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/rasa-environmentd.service %{buildroot}%{_unitdir}

%post
%systemd_post rasa-environmentd.service

%preun
%systemd_preun rasa-environmentd.service

%postun
%systemd_postun_with_restart rasa-environmentd.service

%files
%defattr(0755,root,root,-)
%{_bindir}/environmentd
%defattr(-,root,root,-)
%{_unitdir}/rasa-environmentd.service
%dir /var/tmp/daemon_home/astropy

%changelog
