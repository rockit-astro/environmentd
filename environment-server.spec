Name:      onemetre-environment-server
Version:   1.8
Release:   1
Url:       https://github.com/warwick-one-metre/environmentd
Summary:   Environment daemon for the Warwick one-metre telescope.
License:   GPL-3.0
Group:     Unspecified
BuildArch: noarch
Requires:  python3, %{?systemd_requires}
BuildRequires: systemd-rpm-macros

%description
Part of the observatory software for the Warwick one-meter telescope.

environmentd aggregates the status of the lower level enviroment daemons over a specified time interval and determines whether it is safe to observe.

%build
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}

%{__install} %{_sourcedir}/environmentd %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/environmentd.service %{buildroot}%{_unitdir}

%pre
%service_add_pre environmentd.service

%post
%service_add_post environmentd.service
%fillup_and_insserv -f -y environmentd.service

# Install python dependencies
# This is horrible, but it seems to be the only way that actually works!
pip3 install Pyro4

%preun
%stop_on_removal environmentd.service
%service_del_preun environmentd.service

%postun
%restart_on_update environmentd.service
%service_del_postun environmentd.service

%files
%defattr(0755,root,root,-)
%{_bindir}/environmentd
%defattr(-,root,root,-)
%{_unitdir}/environmentd.service

%changelog
