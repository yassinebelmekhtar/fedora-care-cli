Name:           fedora-care-cli
Version:        1.1.0
Release:        1%{?dist}
Summary:        Fedora Linux maintenance and system monitoring CLI tool

License:        MIT
URL:            https://github.com/selinihtyr/fedora-care-cli
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  pyproject-rpm-macros

Requires:       python3-click >= 8.0
Requires:       python3-psutil >= 5.9
Requires:       python3-rich >= 13.0
Requires:       systemd
Requires:       dnf

%description
FedCare is a Fedora-focused system maintenance CLI tool that provides
health monitoring, service management, network diagnostics, log analysis,
update checking, cleanup operations, config backups, and boot performance
analysis. All commands support both human-readable table output and
machine-readable JSON.

%prep
%autosetup -n %{name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files fedcare

%files -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/fedcare

%changelog
* Tue Jan 28 2026 selinihtyr <selinihtyr@fedoraproject.org> - 1.1.0-1
- Add restore command to recover config files from backups

* Tue Jan 28 2026 selinihtyr <selinihtyr@fedoraproject.org> - 1.0.0-1
- Initial RPM package release
