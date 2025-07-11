Name:      rockit-environment
Version:   %{_version}
Release:   1%{dist}
Summary:   Environment aggregration daemon
Url:       https://github.com/rockit-astro/environmentd
License:   GPL-3.0
BuildArch: noarch

%description


%build
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}/etc/bash_completion.d
mkdir -p %{buildroot}%{_sysconfdir}/environmentd
mkdir -p %{buildroot}%{_udevrulesdir}

%{__install} %{_sourcedir}/environment %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/environmentd %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/environmentd@.service %{buildroot}%{_unitdir}
%{__install} %{_sourcedir}/completion/environment %{buildroot}/etc/bash_completion.d

%{__install} %{_sourcedir}/lapalma.json %{buildroot}%{_sysconfdir}/environmentd
%{__install} %{_sourcedir}/warwick.json %{buildroot}%{_sysconfdir}/environmentd
%{__install} %{_sourcedir}/ngts.json %{buildroot}%{_sysconfdir}/environmentd
%{__install} %{_sourcedir}/portable.json %{buildroot}%{_sysconfdir}/environmentd
%{__install} %{_sourcedir}/pdt.json %{buildroot}%{_sysconfdir}/environmentd

%package server
Summary:  Environment server
Group:    Unspecified
Requires: python3-rockit-environment
%description server

%files server
%defattr(0755,root,root,-)
%{_bindir}/environmentd
%defattr(0644,root,root,-)
%{_unitdir}/environmentd@.service

%package client
Summary:  Environment client
Group:    Unspecified
Requires: python3-rockit-environment
%description client

%files client
%defattr(0755,root,root,-)
%{_bindir}/environment
/etc/bash_completion.d/environment

%package data-lapalma
Summary: Environment data for La Palma telescopes
Group:   Unspecified
%description data-lapalma

%files data-lapalma
%defattr(0644,root,root,-)
%{_sysconfdir}/environmentd/lapalma.json

%package data-warwick
Summary: Environment data for Windmill Hill observatory
Group:   Unspecified
%description data-warwick

%files data-warwick
%defattr(0644,root,root,-)
%{_sysconfdir}/environmentd/warwick.json

%package data-ngts
Summary: Environment data for NGTS
Group:   Unspecified
%description data-ngts

%files data-ngts
%defattr(0644,root,root,-)
%{_sysconfdir}/environmentd/ngts.json

%package data-portable
Summary: Environment data for portable telescope
Group:   Unspecified
%description data-portable

%files data-portable
%defattr(0644,root,root,-)
%{_sysconfdir}/environmentd/portable.json

%package data-pdt
Summary: Environment data for the PDT
Group:   Unspecified
%description data-pdt

%files data-pdt
%defattr(0644,root,root,-)
%{_sysconfdir}/environmentd/pdt.json

%changelog
