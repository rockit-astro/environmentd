Name:      onemetre-environment-server
Version:   3.0.0
Release:   0
Url:       https://github.com/warwick-one-metre/environmentd
Summary:   Environment daemon for the Warwick one-metre telescope.
License:   GPL-3.0
Group:     Unspecified
BuildArch: noarch
%if 0%{?suse_version}
Requires:  python3, python34-Pyro4, python34-warwick-observatory-common, python34-warwick-w1m-environment, observatory-log-client, %{?systemd_requires}
BuildRequires: systemd-rpm-macros
%endif
%if 0%{?centos_ver}
Requires:  python34, python34-Pyro4, python34-warwick-observatory-common, python34-warwick-w1m-environment, observatory-log-client, %{?systemd_requires}
%endif

%description
Part of the observatory software for the Warwick one-meter telescope.

environmentd aggregates the status of the lower level enviroment daemons over a specified time interval and determines whether it is safe to observe.

%build
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}

%{__install} %{_sourcedir}/environmentd %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/environmentd.service %{buildroot}%{_unitdir}

%pre
%if 0%{?suse_version}
%service_add_pre environmentd.service
%endif

%post
%if 0%{?suse_version}
%service_add_post environmentd.service
%endif
%if 0%{?centos_ver}
%systemd_post environmentd.service
%endif

%preun
%if 0%{?suse_version}
%stop_on_removal environmentd.service
%service_del_preun environmentd.service
%endif
%if 0%{?centos_ver}
%systemd_preun environmentd.service
%endif

%postun
%if 0%{?suse_version}
%restart_on_update environmentd.service
%service_del_postun environmentd.service
%endif
%if 0%{?centos_ver}
%systemd_postun_with_restart environmentd.service
%endif

%files
%defattr(0755,root,root,-)
%{_bindir}/environmentd
%defattr(-,root,root,-)
%{_unitdir}/environmentd.service

%changelog
