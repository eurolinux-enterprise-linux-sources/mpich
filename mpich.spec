%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Summary:	A high-performance implementation of MPI
Name:		mpich
Version:	3.0.4
Release:	8%{?dist}
License:	MIT
Group:		Development/Libraries
URL:		http://www.mpich.org

# Source0 derived from
# Source0:	http://www.mpich.org/static/downloads/%{version}/%{name}-%{version}.tar.gz
# by
# rm -r src/mpid/pamid
# vi src/mpid/Makefile*
#  and remove references to pamid
# rm -r src/mpid/ch3/channels/nemesis/netmod/scif
# vi src/src/mpid/ch3/channels/nemesis/netmod/Makefile*
#  and remove references to scif
# rm -r src/pm/hydra/tools/topo/hwloc/hwloc
# vi src/pm/hydra/tools/topo/hwloc/Makefile.mk
#  and remove references to hwloc
# rm `find * -name 'Makefile.in' -print | grep -v doc/ | grep -v src/mpi/romio/mpi2-other/`
# rm -r contrib www
# rm src/mpi/romio/test/external32.c
# rm `find * -name ar-lib -o -name compile -o -name config.guess -o -name config.sub -o -name depcomp -o -name missing -o -name configure -o -name .state-cache -o -name aclocal.mp -o -name libtool.m4`
# rm README.envvar maint/createcoverage maint/getcoverage src/include/mpichconf.h.in src/include/mpich_param_vals.h src/pm/hydra/include/hydra_config.h.in src/util/logging/common/state_names.h src/util/param/param_vals.c subsys_include.m4
#  more extensive changes need to actually build are included in the mpich-3.0.4-rh.patch file
Source0: %{name}-%{version}-rh.tar.gz
Source1:	mpich.macros
# Patch0:		mpich-modules.patch
Patch0: mpich-3.0.4-rh.patch
Patch1: mpich-3.0.4-module.patch

BuildRequires:	libXt-devel, bison, flex, libuuid-devel
BuildRequires:	gcc-gfortran
BuildRequires:  hwloc-devel >= 1.5
BuildRequires:	perl, python, perl-Digest-MD5, hwloc-devel
BuildRequires:	automake autoconf libtool gettext
%ifnarch s390 s390x %{arm}
BuildRequires:	valgrind-devel
%endif
Provides:	mpi
Obsoletes:	mpich2
Obsoletes:	%{name}-libs < 1.1.1
Obsoletes:	%{name}-mpd < 1.4.1
Requires:	environment-modules
Requires:	chkconfig
#Requires chkconfig for /usr/sbin/alternatives

%description
MPICH is a high-performance and widely portable implementation of the
MPI standard (MPI-1, MPI-2 and MPI-3). This release has all MPI-2.2 functions
and features required by the standard with the exeption of support for the
"external32" portable I/O format and user-defined data representations for I/O.

The mpich binaries in this RPM packages were configured to use the default
process manager (Hydra) using the default device (ch3). The ch3 device
was configured with support for the nemesis channel that allows for
shared-memory and TCP/IP sockets based communication.

This build also include support for using the 'module environment' to select
which MPI implementation to use when multiple implementations are installed.
If you want MPICH2 support to be automatically loaded, you need to install the
mpich-autoload package.

%package autoload
Summary:	Load mpich automatically into profile
Group:		System Environment/Base
Requires:	mpich = %{version}-%{release}

%description autoload
This package contains profile files that make mpich automatically loaded.

%package devel
Summary:	Development files for mpich
Group:		Development/Libraries
Provides:	%{name}-devel-static = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Requires:	pkgconfig
Requires:	gcc-gfortran
Requires(pre):	chkconfig
#Requires chkconfig for /usr/sbin/alternatives

%description devel
Contains development headers and libraries for mpich

%package doc
Summary:	Documentations and examples for mpich
Group:		Documentation
BuildArch:	noarch
Requires:	%{name}-devel = %{version}-%{release}

%description doc
Contains documentations, examples and manpages for mpich

# We only compile with gcc, but other people may want other compilers.
# Set the compiler here.
%{!?opt_cc: %global opt_cc gcc}
%{!?opt_fc: %global opt_fc gfortran}
%{!?opt_f77: %global opt_f77 gfortran}
# Optional CFLAGS to use with the specific compiler...gcc doesn't need any,
# so uncomment and undefine to NOT use
%{!?opt_cc_cflags: %global opt_cc_cflags %{optflags}}
%{!?opt_fc_fflags: %global opt_fc_fflags %{optflags}}
#%{!?opt_fc_fflags: %global opt_fc_fflags %{optflags} -I%{_fmoddir}}
%{!?opt_f77_fflags: %global opt_f77_fflags %{optflags}}

%ifarch s390
%global m_option -m31
%else
%global m_option -m%{__isa_bits}
%endif

%ifarch %{arm} aarch64
%global m_option ""
%endif

%ifarch %{ix86} x86_64
%global selected_channels ch3:nemesis
%else
%global selected_channels ch3:sock
%endif

%ifarch x86_64 ia64 ppc64 s390x sparc64
%global priority 41
%else
%global priority 40
%endif

%ifarch %{ix86} x86_64 s390 %{arm}
%global XFLAGS -fPIC
%endif

%prep
%setup -q
# % patch0 -p0 -b .modu
%patch0 -p1 -b .rh
%patch1 -p1 -b .module
./autogen.sh
cd src/pm/hydra && ./autogen.sh && cd ../../..

%build
%configure	\
	--enable-sharedlibs=gcc					\
	--enable-shared						\
	--enable-lib-depend					\
	--disable-rpath						\
	--enable-fc						\
	--with-device=%{selected_channels}			\
	--with-pm=hydra:gforker					\
	--sysconfdir=%{_sysconfdir}/%{name}-%{_arch}		\
	--includedir=%{_includedir}/%{name}-%{_arch}		\
	--bindir=%{_libdir}/%{name}/bin				\
	--libdir=%{_libdir}/%{name}/lib				\
	--datadir=%{_datadir}/%{name}				\
	--mandir=%{_mandir}/%{name}				\
	--docdir=%{_datadir}/%{name}/doc			\
	--htmldir=%{_datadir}/%{name}/doc			\
	--with-hwloc-prefix=system				\
	FC=%{opt_fc}						\
	F77=%{opt_f77}						\
	CFLAGS="%{m_option} %{optflags} %{?XFLAGS}"			\
	CXXFLAGS="%{m_option} %{optflags} %{?XFLAGS}"			\
	FCFLAGS="%{m_option} %{optflags} %{?XFLAGS}"			\
	FFLAGS="%{m_option} %{optflags} %{?XFLAGS}"			\
	LDFLAGS='-Wl,-z,noexecstack'				\
	MPICH2LIB_CFLAGS="%{?opt_cc_cflags}"			\
	MPICH2LIB_CXXFLAGS="%{optflags}"			\
	MPICH2LIB_FCFLAGS="%{?opt_fc_fflags}"			\
	MPICH2LIB_FFLAGS="%{?opt_f77_fflags}"
#	MPICH2LIB_LDFLAGS='-Wl,-z,noexecstack'			\
#	MPICH2_MPICC_FLAGS="%{m_option} -O2 %{?XFLAGS}"	\
#	MPICH2_MPICXX_FLAGS="%{m_option} -O2 %{?XFLAGS}"	\
#	MPICH2_MPIFC_FLAGS="%{m_option} -O2 %{?XFLAGS}"	\
#	MPICH2_MPIF77_FLAGS="%{m_option} -O2 %{?XFLAGS}"
#	--with-openpa-prefix=embedded				\

#	FCFLAGS="%{?opt_fc_fflags} -I%{_fmoddir}/%{name} %{?XFLAGS}"	\
#make %{?_smp_mflags} doesn't work
make VERBOSE=1

%install
make DESTDIR=%{buildroot} install

# Workaround 1.4.1 broken destdir
for fichier in mpif77 mpif90 mpicxx mpicc ; do
  sed -i 's#'%{buildroot}'##' %{buildroot}%{_libdir}/%{name}/bin/$fichier
  sed -i 's#'%{buildroot}'##' %{buildroot}%{_sysconfdir}/%{name}-%{_arch}/$fichier.conf
done

mv %{buildroot}%{_libdir}/%{name}/lib/pkgconfig %{buildroot}%{_libdir}/
chmod -x %{buildroot}%{_libdir}/pkgconfig/*.pc

mkdir -p %{buildroot}/%{_fmoddir}/%{name}-%{_arch}
#mv  %{buildroot}%{_includedir}/%{name}/*.mod %{buildroot}/%{_fmoddir}/%{name}/

# Install the module file
mkdir -p %{buildroot}%{_sysconfdir}/modulefiles/mpi
mkdir -p %{buildroot}%{python_sitearch}/%{name}
sed -e 's#@LIBDIR@#%{_libdir}/%{name}#g;s#@ETCDIR@#%{_sysconfdir}/%{name}-%{_arch}#g;s#@FMODDIR@#%{_fmoddir}/%{name}-%{_arch}#g;s#@INCDIR@#%{_includedir}/%{name}-%{_arch}#g;s#@MANDIR@#%{_mandir}/%{name}#g;s#@PYSITEARCH@#%{python_sitearch}/%{name}#g;s#@COMPILER@#%{name}-%{_arch}%{?_cc_name_suffix}#g;s#@SUFFIX@#%{?_cc_name_suffix}_%{name}#g' src/packaging/envmods/mpich.module > %{buildroot}%{_sysconfdir}/modulefiles/mpi/%{name}-%{_arch}

mkdir -p %{buildroot}%{_sysconfdir}/profile.d
cat << EOF > %{buildroot}%{_sysconfdir}/profile.d/mpich-%{_arch}.sh
# Load mpich environment module
module load mpi/%{name}-%{_arch}
EOF
cp -p %{buildroot}%{_sysconfdir}/profile.d/mpich-%{_arch}.{sh,csh}

# Install the RPM macro
mkdir -p %{buildroot}%{_sysconfdir}/rpm
cp -pr %{SOURCE1} %{buildroot}%{_sysconfdir}/rpm/macros.%{name}

# Silence rpmlint
sed -i '/^#! \//,1 d' %{buildroot}%{_sysconfdir}/%{name}-%{_arch}/mpi*.conf

# The uninstall script here is not needed/necesary for rpm packaging
rm -rf %{buildroot}%{_sbindir}/mpe*

find %{buildroot} -type f -name "*.la" -exec rm -f {} ';'
rm -f %{buildroot}%{_libdir}/%{name}/lib/lib{*mpich*,opa,mpl}.a

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%pre
if [ $1 -gt 1 ] ; then
	if [ -e %{_bindir}/mpiexec.py ] ; then
		/usr/sbin/alternatives --remove mpi-run %{_bindir}/mpiexec.py
	fi
fi

%pre devel
if [ $1 -gt 1 ] ; then
# Remove the old alternative
	if [ -e %{_bindir}/mp%{__isa_bits}-mpicc ] ; then
	/usr/sbin/alternatives --remove mpicc %{_bindir}/mp%{__isa_bits}-mpicc
	fi
fi

%files
%defattr(-,root,root,-)
%doc CHANGES COPYRIGHT README RELEASE_NOTES
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/lib
%dir %{_libdir}/%{name}/bin
%{_libdir}/%{name}/lib/*.so.*
%{_libdir}/%{name}/bin/hydra*
%{_libdir}/%{name}/bin/mpichversion
%{_libdir}/%{name}/bin/mpiexec*
%{_libdir}/%{name}/bin/mpirun
%dir %{python_sitearch}/%{name}
%dir %{_fmoddir}/%{name}-%{_arch}
%{_libdir}/%{name}/bin/parkill
%dir %{_mandir}/%{name}
%dir %{_mandir}/%{name}/man1
%{_mandir}/%{name}/man1/mpiexec*
%dir %{_sysconfdir}/modulefiles/mpi
%{_sysconfdir}/modulefiles/mpi/%{name}-%{_arch}

%files autoload
%defattr(-,root,root,-)
%{_sysconfdir}/profile.d/mpich-%{_arch}.*

%files devel
%defattr(-,root,root,-)
%{_libdir}/%{name}/bin/mpicc
%{_libdir}/%{name}/bin/mpicxx
%{_libdir}/%{name}/bin/mpic++
%{_libdir}/%{name}/bin/mpif*
%{_mandir}/%{name}/man1/mpic*
%{_mandir}/%{name}/man1/mpif*
%config %{_sysconfdir}/%{name}-%{_arch}/
%{_includedir}/%{name}-%{_arch}/
#%{_fmoddir}/%{name}/
%{_libdir}/%{name}/lib/*.so
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/pkgconfig/openpa.pc
%config %{_sysconfdir}/rpm/macros.%{name}

%files doc
%defattr(-,root,root,-)
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/doc/
%{_mandir}/%{name}/man3/

%changelog
* Wed Sep 10 2014 Yaakov Selkowitz <yselkowi@redhat.com> - 3.0.4-8
- Do not use -m64 on AArch64
  Resolves: rhbz1077315

* Mon Mar 3 2014 Jay Fenlason <fenlason@redhat.com> - 3.0.4-7
- Update build flags to fix
  Resolves: rhbz1070778

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 3.0.4-6
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 3.0.4-5
- Mass rebuild 2013-12-27

* Fri Oct 4 2013 Jay Fenlason <fenlason@redhat.com> 3.0.4-4.el7
- Fix the module file to contain all the definitions we expect.
  Resolves: rhbz1001469

* Wed Oct 2 2013 Jay Fenlason <fenlason@redhat.com> 3.0.4-3.el7
- Fix macros.mpich
  Resolves: rhbz1001469

* Fri Sep 6 2013 Jay Fenlason <fenlason@redhat.com> 3.0.4-1.el7
- Initial import for RHEL, using sanitized source tarball.

