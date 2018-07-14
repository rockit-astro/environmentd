Name:      onemetre-environment-server
Version:   3.1.2
Release:   0
Url:       https://github.com/warwick-one-metre/environmentd
Summary:   Environment daemon for the Warwick one-metre telescope.
License:   GPL-3.0
Group:     Unspecified
BuildArch: noarch
Requires:  python34, python34-Pyro4, python34-pyephem, python34-warwick-observatory-common,
Requires:  python34-warwick-observatory-environment, observatory-log-client, %{?systemd_requires}

%description
Part of the observatory software for the Warwick one-meter telescope.

environmentd aggregates the status of the lower level enviroment daemons over a specified time interval and determines whether it is safe to observe.

%build
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}

%{__install} %{_sourcedir}/environmentd %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/environmentd.service %{buildroot}%{_unitdir}

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

%changelog
