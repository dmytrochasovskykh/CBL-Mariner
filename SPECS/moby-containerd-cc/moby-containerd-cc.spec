%global debug_package %{nil}
%define upstream_name containerd-cc
%define upstream_repo confidential-containers-containerd
%define commit_hash 4a2809f776500dfb8e4ed33db7f4e05ed68edfbf

Summary: Industry-standard container runtime for confidential containers
Name: moby-%{upstream_name}
Version: 1.7.1
Release: 1%{?dist}
License: ASL 2.0
Group: Tools/Container
URL: https://www.containerd.io
Vendor: Microsoft Corporation
Distribution: Mariner

Source0:  https://github.com/microsoft/confidential-containers-containerd/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1: containerd.service
Source2: containerd.toml

%{?systemd_requires}

BuildRequires: btrfs-progs-devel
BuildRequires: git
BuildRequires: golang >= 1.19.0
BuildRequires: go-md2man
BuildRequires: make
BuildRequires: systemd-rpm-macros

Requires: moby-runc >= 1.1.0

Conflicts: moby-containerd
Conflicts: moby-engine <= 3.0.10

Obsoletes: containerd
Obsoletes: containerd-io

%description
This is the containerd runtime meant for use with confidential containers

%prep
%autosetup -p1 -n %{upstream_repo}-%{version}

%build
export BUILDTAGS="-mod=vendor"
make VERSION="%{version}" REVISION="%{commit_hash}" binaries man

%check
export BUILDTAGS="-mod=vendor"
make VERSION="%{version}" REVISION="%{commit_hash}" test

%install
make VERSION="%{version}" REVISION="%{commit_hash}" DESTDIR="%{buildroot}" PREFIX="/usr" install install-man

mkdir -p %{buildroot}/%{_unitdir}
install -D -p -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/containerd.service
install -D -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/containerd/config.toml

%post
%systemd_post containerd.service

if [ $1 -eq 1 ]; then # Package install
	systemctl enable containerd.service > /dev/null 2>&1 || :
	systemctl start containerd.service > /dev/null 2>&1 || :
fi

%preun
%systemd_preun containerd.service

%postun
%systemd_postun_with_restart containerd.service

%files
%license LICENSE NOTICE
%{_bindir}/*
%{_mandir}/*
%config(noreplace) %{_unitdir}/containerd.service
%config(noreplace) %{_sysconfdir}/containerd/config.toml

%changelog
*   Mon May 22 2023 Dallas Delaney <dadelan@microsoft.com> - 1.7.1-1
-   Fix unit test arguments for TestSnapshotterFromPodSandboxConfig

*   Wed May 17 2023 Dallas Delaney <dadelan@microsoft.com> - 1.7.0-2
-   Add build version dependency on golang

*   Tue Apr 25 2023 Dallas Delaney <dadelan@microsoft.com> - 1.7.0-1
-   Add initial spec
-   License verified.
-   Original version for CBL-Mariner
