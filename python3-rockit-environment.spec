Name:           python3-rockit-environment
Version:        %{_version}
Release:        1%{dist}
License:        GPL3
Summary:        Common backend code for the environment daemon.
Url:            https://github.com/rockit-astro/environmentd
BuildArch:      noarch
BuildRequires:  python3-devel

%description

%prep
rsync -av --exclude=build --exclude=.git --exclude=.github .. .

%generate_buildrequires
%pyproject_buildrequires -R

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files rockit

%files -f %{pyproject_files}
