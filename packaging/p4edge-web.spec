%{!?srvdir: %global srvdir /srv/p4edge}
Name:           p4edge-web
Version:        0.0.0
Release:        0%{?dist}
Summary:        Web UI for P4edge
License:        Apache 2.0
URL:            https://github.com/p4edge/ui
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3, python3-pip, lm-sensors, ifstat
BuildRequires:  debbuild-macros-systemd
Packager:       Dávid Kis <kidraai@.inf.elte.hu>

%description
Web UI for P4edge

%prep
%autosetup

%build

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{srvdir}
cp -r config/ %{buildroot}%{srvdir}
cp -r dashboard/ %{buildroot}%{srvdir}
cp -r terminal/ %{buildroot}%{srvdir}
cp -r fixtures/ %{buildroot}%{srvdir}
cp gunicorn-cfg.py %{buildroot}%{srvdir}
cp manage.py %{buildroot}%{srvdir}
cp poetry.lock %{buildroot}%{srvdir}
cp pyproject.toml %{buildroot}%{srvdir}
cp requirements.txt %{buildroot}%{srvdir}
cp .editorconfig %{buildroot}%{srvdir}
cp dummy_ctrl_plane_connection.py %{buildroot}%{srvdir}
cp generate-statistics.py %{buildroot}%{srvdir}

mkdir -p %{buildroot}%{_unitdir}
cp packaging/%{name}.service %{buildroot}%{_unitdir}
cp packaging/%{name}-genstat.service %{buildroot}%{_unitdir}
cp packaging/%{name}-dummy-ctrl-plane.service %{buildroot}%{_unitdir}

%post
cat > %{srvdir}/.env << EOF
DEBUG=TRUE
ALLOWED_HOSTS=["*"]
SECRET_KEY=`python3 -c "import secrets; print(secrets.token_urlsafe())"`
SQLITE_PATH=%{srvdir}/db.sqlite3
EOF

python3 -m pip install -r %{srvdir}/requirements.txt

cd %{srvdir}
python3 -m django migrate --settings=config.settings
python3 -m django loaddata fixtures/users.json --settings=config.settings

%systemd_post %{name}.service
%systemd_post %{name}-genstat.service
%systemd_post %{name}-dummy-ctrl-plane.service

%preun
%systemd_preun %{name}.service
%systemd_preun %{name}-genstat.service
%systemd_preun %{name}-dummy-ctrl-plane.service

%postun
%systemd_postun %{name}.service
%systemd_postun %{name}-genstat.service
%systemd_postun %{name}-dummy-ctrl-plane.service

%files
%{srvdir}/*
%{srvdir}/.editorconfig
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-genstat.service
%{_unitdir}/%{name}-dummy-ctrl-plane.service
