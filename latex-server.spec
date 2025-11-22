Name:           latex-server
Version:        2.0.0
Release:        1%{?dist}
Summary:        FastAPI-based HTTP server for compiling LaTeX documents to PDF

License:        MIT
URL:            https://github.com/ferdiu/latex-server
Source0:        %{url}/archive/v%{version}/latex-server-%{version}.tar.gz

BuildArch:      noarch

# Python build deps
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-fastapi
BuildRequires:  python3-uvicorn
BuildRequires:  python3-uvicorn+standard
BuildRequires:  python3-pydantic
BuildRequires:  python3-wheel

# Runtime deps
Requires:       python3
Requires:       python3-fastapi >= 0.109.0
Requires:       python3-uvicorn >= 0.27.0
Requires:       python3-uvicorn+standard >= 0.27.0
Requires:       python3-pydantic >= 2.5.0

# Basic LaTeX requirements
Requires:       /usr/bin/pdflatex
Requires:       /usr/bin/bibtex

# Recommendations for full functionality
Recommends:     texlive-scheme-full
Recommends:     texlive-latex
Recommends:     texlive-latex-recommended
Recommends:     texlive-latex-extra
Recommends:     texlive-fonts-recommended
Recommends:     texlive-fonts-extra
Recommends:     texlive-bibtex-extra
Recommends:     texlive-science
Recommends:     texlive-xetex
Recommends:     texlive-luatex

Suggests:       texlive-publishers texlive-pictures texlive-pstricks texlive-games


%global _description %{expand:
LaTeX Compilation Server is a FastAPI-based HTTP service that compiles
LaTeX projects to PDF. It supports multi-pass compilation, BibTeX,
multi-file projects, and includes a hardened systemd service using
DynamicUser for isolation.
}

%description %_description



####################################
# MAIN PYTHON PACKAGE
####################################

%package -n python3-latex-server
Summary: %{summary}
%description -n python3-latex-server %_description



####################################
# PREP
####################################

%prep
%autosetup -p1 -n latex-server-%{version}
%generate_buildrequires
%pyproject_buildrequires



####################################
# BUILD
####################################

%build
%pyproject_wheel



####################################
# INSTALL
####################################

%install
%pyproject_install
%pyproject_save_files -l latex_server


### Systemd service ###

install -d %{buildroot}/usr/lib/systemd/system
cat > %{buildroot}/usr/lib/systemd/system/latex-server.service << 'EOF'
[Unit]
Description=LaTeX Compilation Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple

DynamicUser=yes

# Persistent directories created by systemd
StateDirectory=latex-server
CacheDirectory=latex-server
LogsDirectory=latex-server

WorkingDirectory=/var/lib/latex-server

EnvironmentFile=-%{_sysconfdir}/latex-server/config.env

ExecStart=/usr/bin/latex-server

Restart=on-failure
RestartSec=5s

# Hardening
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
PrivateUsers=yes
ProtectSystem=strict
ProtectHome=read-only
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectKernelLogs=yes
ProtectClock=yes
LockPersonality=yes
MemoryDenyWriteExecute=yes
RestrictRealtime=yes
RestrictNamespaces=yes
RestrictSUIDSGID=yes
CapabilityBoundingSet=
AmbientCapabilities=
SystemCallArchitectures=native
SystemCallFilter=@system-service

ReadWritePaths=/var/lib/latex-server

[Install]
WantedBy=multi-user.target
EOF


### tmpfiles.d ###

install -d %{buildroot}/usr/lib/tmpfiles.d
cat > %{buildroot}/usr/lib/tmpfiles.d/latex-server.conf << 'EOF'
d /var/lib/latex-server - - - -
d /var/cache/latex-server - - - -
d /var/log/latex-server - - - -
EOF


### Configuration directory ###

install -d %{buildroot}%{_sysconfdir}/latex-server

cat > %{buildroot}%{_sysconfdir}/latex-server/config.env << 'EOF'
LATEX_SERVER_HOST=127.0.0.1
LATEX_SERVER_PORT=9080
LATEX_SERVER_LOG_LEVEL=INFO
LATEX_SERVER_MAX_COMPILATIONS=5
LATEX_SERVER_COMMAND_TIMEOUT=60
LATEX_SERVER_LATEX_COMMAND=pdflatex
LATEX_SERVER_BIBTEX_COMMAND=bibtex
EOF



####################################
# CHECK
####################################

%check
%pyproject_check_import



####################################
# SCRIPTLETS
####################################

%post -n python3-latex-server
%systemd_post latex-server.service

%preun -n python3-latex-server
%systemd_preun latex-server.service

%postun -n python3-latex-server
%systemd_postun_with_restart latex-server.service



####################################
# FILES
####################################

%files -n python3-latex-server -f %{pyproject_files}
%{_bindir}/latex-server
/usr/lib/systemd/system/latex-server.service
/usr/lib/tmpfiles.d/latex-server.conf
%dir %{_sysconfdir}/latex-server
%config(noreplace) %{_sysconfdir}/latex-server/config.env
%doc README.md SETUP.md


%changelog
* Sat Nov 22 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 2.0.0-1
- Update protocol to support binary files

* Sat Nov 22 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 1.0.3-1
- Initial RPM release
- Added tmpfiles.d persistent state directories
- Hardened systemd service
- FastAPI-based LaTeX compilation server
- Automatic multi-pass compilation support
- BibTeX integration
- RESTful JSON API
- Systemd service integration
- Security hardening with dedicated user
- Configurable via environment variables