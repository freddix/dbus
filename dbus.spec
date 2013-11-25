Summary:	D-BUS message bus
Name:		dbus
Version:	1.6.18
Release:	1
License:	AFL v2.1 or GPL v2
Group:		Libraries
Source0:	http://dbus.freedesktop.org/releases/dbus/%{name}-%{version}.tar.gz
# Source0-md5:	b02e9c95027a416987b81f9893831061
Source1:	%{name}-tmpfiles.conf
Patch0:		%{name}-nolibs.patch
Patch1:		%{name}-fix-sba-for-dbus-activation.patch
URL:		http://www.freedesktop.org/Software/dbus
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	expat-devel
BuildRequires:	libtool
BuildRequires:	pkg-config
BuildRequires:	systemd-devel
BuildRequires:	xorg-libX11-devel
Requires(post,preun,postun):	systemd-units
Requires(postun):	coreutils
Requires(pre):	pwdutils
Requires:	%{name}-libs = %{version}-%{release}
Provides:	group(messagebus)
Provides:	user(messagebus)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libexecdir	%{_libdir}/%{name}-1.0

%description
D-BUS is a system for sending messages between applications. It is
used both for the systemwide message bus service, and as a
per-user-login-session messaging facility.

%package libs
Summary:	D-BUS libraries
Group:		Libraries

%description libs
D-BUS libraries.

%package devel
Summary:	Header files for D-BUS
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for D-BUS.

%package launch
Summary:	Utility to start a message bus from a shell script
Group:		Applications
Requires:	%{name} = %{version}-%{release}

%description launch
The dbus-launch command is used to start a session bus instance
of dbus-daemon from a shell script. It would normally be called
from a user's  login scripts. Unlike the daemon itself, dbus-launch
exits, so backticks or the $() construct can be used to read
information from dbus-launch.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-asserts					\
	--disable-dnotify					\
	--disable-silent-rules					\
	--disable-static					\
	--disable-tests						\
	--enable-systemd					\
	--enable-x11-autolaunch					\
	--with-console-auth-dir=/run/console/			\
	--with-system-pid-file=/run/dbus/pid			\
	--with-system-socket=/run/dbus/system_bus_socket	\
	--with-systemdsystemunitdir=%{systemdunitdir}		\
	--with-xml=expat
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_datadir}/dbus-1/{interfaces,services}	\
	$RPM_BUILD_ROOT%{systemdtmpfilesdir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf

rm -rf $RPM_BUILD_ROOT%{_docdir}/dbus/api

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 100 messagebus
%useradd -u 100 -d /usr/share/empty -s /usr/bin/false -c "System message bus" -g messagebus messagebus

%post
export NORESTART="yes"
%systemd_post messagebus.service

%preun
%systemd_preun messagebus.service

%postun
if [ "$1" = "0" ]; then
	%userremove messagebus
	%groupremove messagebus
fi
%systemd_postun

%post	libs -p /usr/sbin/ldconfig
%postun	libs -p /usr/sbin/ldconfig

%files
%defattr(644,root,root,755)

%dir %{_sysconfdir}/dbus-1
%dir %{_sysconfdir}/dbus-1/session.d
%dir %{_sysconfdir}/dbus-1/system.d
%dir /var/lib/dbus

%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dbus-1/*.conf
%{systemdtmpfilesdir}/dbus.conf

%attr(4750,root,messagebus) %{_libexecdir}/dbus-daemon-launch-helper
%attr(755,root,root) %{_bindir}/dbus-cleanup-sockets
%attr(755,root,root) %{_bindir}/dbus-daemon
%attr(755,root,root) %{_bindir}/dbus-monitor
%attr(755,root,root) %{_bindir}/dbus-send
%attr(755,root,root) %{_bindir}/dbus-uuidgen

%dir %{_prefix}/lib/systemd/system/dbus.target.wants
%{_prefix}/lib/systemd/system/dbus.service
%{_prefix}/lib/systemd/system/dbus.socket
%{_prefix}/lib/systemd/system/dbus.target.wants/dbus.socket
%{_prefix}/lib/systemd/system/multi-user.target.wants/dbus.service
%{_prefix}/lib/systemd/system/sockets.target.wants/dbus.socket

%{_mandir}/man1/dbus-cleanup-sockets.1*
%{_mandir}/man1/dbus-daemon.1*
%{_mandir}/man1/dbus-monitor.1*
%{_mandir}/man1/dbus-send.1*
%{_mandir}/man1/dbus-uuidgen.1*

%files libs
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog NEWS README doc/TODO
%attr(755,root,root) %ghost %{_libdir}/libdbus-1.so.?
%attr(755,root,root) %{_libdir}/libdbus-1.so.*.*.*

%dir %{_datadir}/dbus-1
%dir %{_datadir}/dbus-1/interfaces
%dir %{_datadir}/dbus-1/services
%dir %{_datadir}/dbus-1/system-services
%dir %{_libdir}/dbus-1.0

%files devel
%defattr(644,root,root,755)
%doc doc/*.{html,txt}
%attr(755,root,root) %{_libdir}/libdbus-1.so
%{_includedir}/dbus*
%{_libdir}/dbus-*/include
%{_pkgconfigdir}/dbus-1.pc

%files launch
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dbus-launch
%{_mandir}/man1/dbus-launch.1*

