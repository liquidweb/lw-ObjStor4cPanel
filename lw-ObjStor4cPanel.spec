%global lw_path /usr/local/lp/bin
%global bin_name lw-ObjStor4cPanel
%global git_repo github.com/jakdept/%{bin_name}
%global goversion 1.8.3
%global builddir ${RPM_BUILD_DIR}

Summary: LiquidWeb Object Storage transporter for cPanel
Name: %{bin_name}
Version: 1.1.0
Release: 0
License: MIT
Group: Applications/System
BuildRoot: %{_topdir}/%{name}-%{version}-%{release}-build
BuildArch: x86_64
Requires: bash
BuildRequires: curl git

%description
A transporter to connect cPanel's backup system to Liquid Web's Object Storage.

%prep
# install go
mkdir -p %{builddir}/go/{src,bin}
mkdir -p %{builddir}/usr/local

if ! go version ; then
  /usr/bin/curl -s -S -L \
    https://storage.googleapis.com/golang/go%{goversion}.linux-amd64.tar.gz|tar \
    xz -C %{builddir}/usr/local
fi

export PATH=%{builddir}/usr/local/go/bin:$PATH
export GOROOT=%{builddir}/usr/local/go
export GOPATH=%{builddir}/go

go get %{git_repo}
go get -t -v %{git_repo}/...

%build
export PATH=%{builddir}/usr/local/go/bin:$PATH
export GOROOT=%{builddir}/usr/local/go
export GOPATH=%{builddir}/go
export GOOS=linux
export GOARCH=amd64

echo 'copying updates to package not in git repository from local'

go install %{git_repo}

%install
export PATH=%{builddir}/usr/local/go/bin:$PATH
export GOROOT=%{builddir}/usr/local/go
export GOPATH=%{builddir}/go

mkdir -p %{buildroot}/%{lw_path}
install -m 0755 ${GOPATH}/bin/%{bin_name} %{buildroot}%{lw_path}

%post
whmapi1 backup_destination_list --output=xml | grep -qF '<name>LW Object Storage</name>'
[[ $? != 0 ]] && whmapi1 backup_destination_add \
  name=LW\ Object\ Storage \
  disabled=1 \
  type=Custom \
  upload_system_backup=on \
  script=%{lw_path}/%{bin_name} \
  host=bucketname \
  path=backup/$(hostname)/ \
  timeout=300 \
  username=username \
  password=changeme > /dev/null
exit 0

# cannot cleanly do preun action - cPanel assigns a random id and does not make
# it easy to find a specific backup destination

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,root,root)
%{lw_path}/%{bin_name}

%changelog
* Wed Aug 23 2017 Jack Hayhurst <jhayhurst@liquidweb.com> - version 1.1.0
- corrected package summary/long name.
- corrected lsdir function so that it now lists folders
- got cPanel backup purging working
- added something to make sure that the backup destination is added just once


* Thu Aug  3 2017 Jack Hayhurst <jhayhurst@liquidweb.com> - version 1.0.0
- finished RPM and bumped version number for final deployment

* Thu Aug  3 2017 Jack Hayhurst <jhayhurst@liquidweb.com> - version 0.5.0
- included some fixes for secteam

* Thu Jul 31 2017 Jack Hayhurst <jhayhurst@liquidweb.com> - version 0.4.0
- renamed the script and rpm

* Thu Apr 13 2017 Jack Hayhurst <jhayhurst@liquidweb.com> - version 0.3
- got rpm version fully working - yay!

* Thu Apr 13 2017 Jack Hayhurst <jhayhurst@liquidweb.com> - version 0.2
- Wrote initial RPM