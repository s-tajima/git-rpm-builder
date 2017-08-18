# nohup rpmbuild -ba --define 'dist .el6_53.wing' git.spec &

# Pass --without docs to rpmbuild if you don't want the documentation

# Leave git-* binaries in %{_bindir} on EL <= 5
%if 0%{?rhel} && 0%{?rhel} <= 5
%global gitcoredir %{_bindir}
%else
%global gitcoredir %{_libexecdir}/git-core
%endif

# Build noarch subpackages and use libcurl-devel on Fedora and EL >= 6
%if 0%{?fedora} || 0%{?rhel} >= 6
%global noarch_sub 1
%global libcurl_devel libcurl-devel
%else
%global noarch_sub 0
%global libcurl_devel curl-devel
%endif

# Build git-emacs, use perl(Error) and perl(Net::SMTP::SSL), require cvsps, and
# adjust git-core obsolete version on Fedora and EL >= 5.  (We don't really
# support EL-4, but folks stuck using it have enough problems, no point making
# it harder on them.)
%if 0%{?fedora} || 0%{?rhel} >= 5
%global emacs_support 1
%global git_core_version 1.5.4.3
%global perl_error 1
%global perl_net_smtp_ssl 1
%global require_cvsps 1
%else
%global emacs_support 0
%global git_core_version 1.5.4.7-4
%global perl_error 0
%global perl_net_smtp_ssl 0
%global require_cvsps 0
%endif

# Patch emacs and tweak docbook spaces on EL-5
%if 0%{?rhel} == 5
%global emacs_old 1
%global docbook_suppress_sp 1
%else
%global emacs_old 0
%global docbook_suppress_sp 0
%endif

# Enable ipv6 for git-daemon, use desktop --vendor option and setup python
# macros on EL <= 5
%if 0%{?rhel} && 0%{?rhel} <= 5
%global enable_ipv6 1
%global use_desktop_vendor 1
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%else
%global enable_ipv6 1
%global use_desktop_vendor 1
%endif

# Use asciidoc-7 on EL <= 4.  Again, we don't support EL-4, but no need to make
# it more difficult to build a modern git there.
%if 0%{?rhel} && 0%{?rhel} <= 4
%global asciidoc7 1
%else
%global asciidoc7 0
%endif

# Only build git-arch for Fedora < 16, where tla is available
%if 0%{?fedora} && 0%{?fedora} < 16
%global arch_support 1
%else
%global arch_support 0
%endif

# Build gnome-keyring git-credential helper on Fedora and RHEL >= 7
%if 0%{?rhel} >= 7 || 0%{?fedora}
%global gnome_keyring 1
%else
%global gnome_keyring 0
%endif

Name:           git
Version:        2.9.0
Release:        1%{?dist}
Summary:        Fast Version Control System
License:        GPLv2
Group:          Development/Tools
URL:            http://git-scm.com/
Source0:        http://git-core.googlecode.com/files/%{name}-%{version}.tar.gz
Source2:        git-init.el
Source3:        git.xinetd.in
Source4:        git.conf.httpd
Source5:        git-gui.desktop
Source6:        gitweb.conf.in

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  desktop-file-utils
%if %{emacs_support}
BuildRequires:  emacs
%endif
BuildRequires:  %{libcurl_devel}
BuildRequires:  expat-devel
BuildRequires:  gettext
BuildRequires:  pcre-devel
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel
%{!?_without_docs:BuildRequires: asciidoc > 6.0.3, xmlto}
%if %{gnome_keyring}
BuildRequires:  libgnome-keyring-devel
%endif

Requires:       less
Requires:       openssh-clients
%if %{perl_error}
Requires:       perl(Error)
%endif
Requires:       perl-Git = %{version}-%{release}
Requires:       rsync
Requires:       zlib

Provides:       git-core = %{version}-%{release}
Obsoletes:      git-core <= %{git_core_version}

# Obsolete git-arch as needed
%if ! %{arch_support}
Obsoletes:      git-arch < %{version}-%{release}
%endif

%description
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

The git rpm installs the core tools with minimal dependencies.  To
install all git packages, including tools for integrating with other
SCMs, install the git-all meta-package.

%package all
Summary:        Meta-package to pull in all git tools
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}
%if %{arch_support}
Requires:       git-arch = %{version}-%{release}
%endif
Requires:       git-cvs = %{version}-%{release}
Requires:       git-email = %{version}-%{release}
Requires:       git-gui = %{version}-%{release}
Requires:       git-svn = %{version}-%{release}
Requires:       git-p4 = %{version}-%{release}
Requires:       gitk = %{version}-%{release}
Requires:       perl-Git = %{version}-%{release}
%if %{emacs_support}
Requires:       emacs-git = %{version}-%{release}
%endif
Obsoletes:      git <= %{git_core_version}

%description all
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

This is a dummy package which brings in all subpackages.

%package daemon
Summary:        Git protocol dæmon
Group:          Development/Tools
Requires:       git = %{version}-%{release}, xinetd
%description daemon
The git dæmon for supporting git:// access to git repositories

%package -n gitweb
Summary:        Simple web interface to git repositories
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}

%description -n gitweb
Simple web interface to track changes in git repositories

%package p4
Summary:        Git tools for working with Perforce depots
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
BuildRequires:  python
Requires:       git = %{version}-%{release}
%description p4
%{summary}.

%package svn
Summary:        Git tools for importing Subversion repositories
Group:          Development/Tools
#%if %{noarch_sub}
#BuildArch:      noarch
#%endif
Requires:       git = %{version}-%{release}, subversion, perl(Term::ReadKey)
%description svn
Git tools for importing Subversion repositories.

%package cvs
Summary:        Git tools for importing CVS repositories
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}, cvs
%if %{require_cvsps}
Requires:       cvsps
Requires:	perl-DBD-SQLite
%endif
%description cvs
Git tools for importing CVS repositories.

%if %{arch_support}
%package arch
Summary:        Git tools for importing Arch repositories
Group:          Development/Tools
BuildArch:      noarch
Requires:       git = %{version}-%{release}, tla
%description arch
Git tools for importing Arch repositories.
%endif

%package email
Summary:        Git tools for sending email
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}, perl-Git = %{version}-%{release}
Requires:       perl(Authen::SASL)
%if %{perl_net_smtp_ssl}
Requires:       perl(Net::SMTP::SSL)
%endif
%description email
Git tools for sending email.

%package gui
Summary:        Git GUI tool
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}, tk >= 8.4
Requires:       gitk = %{version}-%{release}
%description gui
Git GUI tool.

%package -n gitk
Summary:        Git revision tree visualiser
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}, tk >= 8.4
%description -n gitk
Git revision tree visualiser.

%package -n perl-Git
Summary:        Perl interface to Git
Group:          Development/Libraries
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}
%if %{perl_error}
BuildRequires:  perl(Error), perl(ExtUtils::MakeMaker)
Requires:       perl(Error)
%endif
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description -n perl-Git
Perl interface to Git.

%package -n perl-Git-SVN
Summary:        Perl interface to Git::SVN
Group:          Development/Libraries
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       git = %{version}-%{release}
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description -n perl-Git-SVN
Perl interface to Git.

%if %{emacs_support}
%package -n emacs-git
Summary:        Git version control system support for Emacs
Group:          Applications/Editors
Requires:       git = %{version}-%{release}
%if %{noarch_sub}
BuildArch:      noarch
Requires:       emacs(bin) >= %{_emacs_version}
%else
Requires:       emacs-common
%endif

%description -n emacs-git
%{summary}.

%package -n emacs-git-el
Summary:        Elisp source files for git version control system support for Emacs
Group:          Applications/Editors
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       emacs-git = %{version}-%{release}

%description -n emacs-git-el
%{summary}.
%endif

%prep
%setup -q

# Use these same options for every invocation of 'make'.
# Otherwise it will rebuild in %%install due to flags changes.
cat << \EOF > config.mak
V = 1
CFLAGS = %{optflags}
BLK_SHA1 = 1
NEEDS_CRYPTO_WITH_SSL = 1
USE_LIBPCRE = 1
ETC_GITCONFIG = %{_sysconfdir}/gitconfig
DESTDIR = %{buildroot}
INSTALL = install -p
GITWEB_PROJECTROOT = %{_var}/lib/git
htmldir = %{_docdir}/%{name}-%{version}
prefix = %{_prefix}
gitwebdir = %{_var}/www/git
EOF

%if "%{gitcoredir}" == "%{_bindir}"
echo gitexecdir = %{_bindir} >> config.mak
%endif

%if %{docbook_suppress_sp}
# This is needed for 1.69.1-1.71.0
echo DOCBOOK_SUPPRESS_SP = 1 >> config.mak
%endif

%if %{asciidoc7}
echo ASCIIDOC7 = 1 >> config.mak
%endif

# Filter bogus perl requires
# packed-refs comes from a comment in contrib/hooks/update-paranoid
cat << \EOF > %{name}-req
#!/bin/sh
%{__perl_requires} $* |\
sed -e '/perl(packed-refs)/d'
EOF

%global __perl_requires %{_builddir}/%{name}-%{version}/%{name}-req
chmod +x %{__perl_requires}

%build
make %{?_smp_mflags} all %{!?_without_docs: doc}

%if %{emacs_support}
make -C contrib/emacs
%endif

%if %{gnome_keyring}
make -C contrib/credential/gnome-keyring/
%endif

make -C contrib/subtree/

# Remove shebang from bash-completion script
sed -i '/^#!bash/,+1 d' contrib/completion/git-completion.bash

%install
rm -rf %{buildroot}
make %{?_smp_mflags} INSTALLDIRS=vendor install %{!?_without_docs: install-doc}

%if %{emacs_support}
%if %{emacs_old}
%global _emacs_sitelispdir %{_datadir}/emacs/site-lisp
%global _emacs_sitestartdir %{_emacs_sitelispdir}/site-start.d
%endif
%global elispdir %{_emacs_sitelispdir}/git
make -C contrib/emacs install \
    emacsdir=%{buildroot}%{elispdir}
for elc in %{buildroot}%{elispdir}/*.elc ; do
    install -pm 644 contrib/emacs/$(basename $elc .elc).el \
    %{buildroot}%{elispdir}
done
install -Dpm 644 %{SOURCE2} \
    %{buildroot}%{_emacs_sitestartdir}/git-init.el
%endif

%if %{gnome_keyring}
install -pm 755 contrib/credential/gnome-keyring/git-credential-gnome-keyring \
    %{buildroot}%{gitcoredir}
%endif

make -C contrib/subtree install
make -C contrib/subtree install-doc

mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
install -pm 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/httpd/conf.d/git.conf
sed "s|@PROJECTROOT@|%{_var}/lib/git|g" \
    %{SOURCE6} > %{buildroot}%{_sysconfdir}/gitweb.conf

find %{buildroot} -type f -name .packlist -exec rm -f {} ';'
find %{buildroot} -type f -name '*.bs' -empty -exec rm -f {} ';'
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} ';'

# Remove remote-helper python libraries and scripts, these are not ready for
# use yet
rm -rf %{buildroot}%{python_sitelib} %{buildroot}%{gitcoredir}/git-remote-testgit

%if ! %{arch_support}
find %{buildroot} Documentation -type f -name 'git-archimport*' -exec rm -f {} ';'
%endif

(find %{buildroot}{%{_bindir},%{_libexecdir}} -type f | grep -vE "archimport|p4|svn|cvs|email|gitk|git-gui|git-citool|git-daemon" | sed -e s@^%{buildroot}@@) > bin-man-doc-files
(find %{buildroot}%{perl_vendorlib} -type f | sed -e s@^%{buildroot}@@) >> perl-git-files
# Split out Git::SVN files
grep Git/SVN perl-git-files > perl-git-svn-files
sed -i "/Git\/SVN/ d" perl-git-files
%if %{!?_without_docs:1}0
(find %{buildroot}%{_mandir} -type f | grep -vE "archimport|p4|svn|git-cvs|email|gitk|git-gui|git-citool|git-daemon|Git" | sed -e s@^%{buildroot}@@ -e 's/$/*/' ) >> bin-man-doc-files
%else
rm -rf %{buildroot}%{_mandir}
%endif

mkdir -p %{buildroot}%{_var}/lib/git
mkdir -p %{buildroot}%{_sysconfdir}/xinetd.d
# On EL <= 5, xinetd does not enable IPv6 by default
enable_ipv6="        # xinetd does not enable IPv6 by default
        flags           = IPv6"
perl -p \
    -e "s|\@GITCOREDIR\@|%{gitcoredir}|g;" \
    -e "s|\@BASE_PATH\@|%{_var}/lib/git|g;" \
%if %{enable_ipv6}
    -e "s|^}|$enable_ipv6\n$&|;" \
%endif
    %{SOURCE3} > %{buildroot}%{_sysconfdir}/xinetd.d/git

# Setup bash completion
mkdir -p %{buildroot}%{_sysconfdir}/bash_completion.d
install -pm 644 contrib/completion/git-completion.bash %{buildroot}%{_sysconfdir}/bash_completion.d/git

# Move contrib/hooks out of %%docdir and make them executable
mkdir -p %{buildroot}%{_datadir}/git-core/contrib
mv contrib/hooks %{buildroot}%{_datadir}/git-core/contrib
chmod +x %{buildroot}%{_datadir}/git-core/contrib/hooks/*
pushd contrib > /dev/null
ln -s ../../../git-core/contrib/hooks
popd > /dev/null

# Install git-prompt.sh
mkdir -p %{buildroot}%{_datadir}/git-core/contrib/completion
install -pm 644 contrib/completion/git-prompt.sh \
    %{buildroot}%{_datadir}/git-core/contrib/completion/

# install git-gui .desktop file
desktop-file-install \
%if %{use_desktop_vendor}
    --vendor fedora \
%endif
    --dir=%{buildroot}%{_datadir}/applications %{SOURCE5}

# find translations
%find_lang %{name} %{name}.lang
cat %{name}.lang >> bin-man-doc-files

# quiet some rpmlint complaints
chmod -R g-w %{buildroot}
find %{buildroot} -name git-mergetool--lib | xargs chmod a-x
rm -f {Documentation/technical,contrib/emacs}/.gitignore
chmod a-x Documentation/technical/api-index.sh
find contrib -type f | xargs chmod -x


%clean
rm -rf %{buildroot}


%files -f bin-man-doc-files
%defattr(-,root,root)
%{_datadir}/git-core/
%dir %{gitcoredir}
%doc COPYING Documentation/*.txt Documentation/RelNotes contrib/
#%doc README COPYING Documentation/*.txt Documentation/RelNotes contrib/
%{!?_without_docs: %doc Documentation/*.html Documentation/docbook-xsl.css}
%{!?_without_docs: %doc Documentation/howto Documentation/technical}
%{_sysconfdir}/bash_completion.d

%files p4
%defattr(-,root,root)
%{gitcoredir}/*p4*
%{gitcoredir}/mergetools/p4merge
%doc Documentation/*p4*.txt
%{!?_without_docs: %{_mandir}/man1/*p4*.1*}
%{!?_without_docs: %doc Documentation/*p4*.html }

%files svn
%defattr(-,root,root)
%{gitcoredir}/*svn*
%doc Documentation/*svn*.txt
%{!?_without_docs: %{_mandir}/man1/*svn*.1*}
%{!?_without_docs: %doc Documentation/*svn*.html }

%files cvs
%defattr(-,root,root)
%doc Documentation/*git-cvs*.txt
%{_bindir}/git-cvsserver
%{gitcoredir}/*cvs*
%{!?_without_docs: %{_mandir}/man1/*cvs*.1*}
%{!?_without_docs: %doc Documentation/*git-cvs*.html }

%if %{arch_support}
%files arch
%defattr(-,root,root)
%doc Documentation/git-archimport.txt
%{gitcoredir}/git-archimport
%{!?_without_docs: %{_mandir}/man1/git-archimport.1*}
%{!?_without_docs: %doc Documentation/git-archimport.html }
%endif

%files email
%defattr(-,root,root)
%doc Documentation/*email*.txt
%{gitcoredir}/*email*
%{!?_without_docs: %{_mandir}/man1/*email*.1*}
%{!?_without_docs: %doc Documentation/*email*.html }

%files gui
%defattr(-,root,root)
%{gitcoredir}/git-gui*
%{gitcoredir}/git-citool
%{_datadir}/applications/*git-gui.desktop
%{_datadir}/git-gui/
%{!?_without_docs: %{_mandir}/man1/git-gui.1*}
%{!?_without_docs: %doc Documentation/git-gui.html}
%{!?_without_docs: %{_mandir}/man1/git-citool.1*}
%{!?_without_docs: %doc Documentation/git-citool.html}

%files -n gitk
%defattr(-,root,root)
%doc Documentation/*gitk*.txt
%{_bindir}/*gitk*
%{_datadir}/gitk
%{!?_without_docs: %{_mandir}/man1/*gitk*.1*}
%{!?_without_docs: %doc Documentation/*gitk*.html }

%files -n perl-Git -f perl-git-files
%defattr(-,root,root)
%exclude %{_mandir}/man3/*Git*SVN*.3pm*
%{!?_without_docs: %{_mandir}/man3/*Git*.3pm*}

%files -n perl-Git-SVN -f perl-git-svn-files
%defattr(-,root,root)
%{!?_without_docs: %{_mandir}/man3/*Git*SVN*.3pm*}

%if %{emacs_support}
%files -n emacs-git
%defattr(-,root,root)
%doc contrib/emacs/README
%dir %{elispdir}
%{elispdir}/*.elc
%{_emacs_sitestartdir}/git-init.el

%files -n emacs-git-el
%defattr(-,root,root)
%{elispdir}/*.el
%endif

%files daemon
%defattr(-,root,root)
%doc Documentation/*daemon*.txt
%config(noreplace)%{_sysconfdir}/xinetd.d/git
%{gitcoredir}/git-daemon
%{_var}/lib/git
%{!?_without_docs: %{_mandir}/man1/*daemon*.1*}
%{!?_without_docs: %doc Documentation/*daemon*.html}

%files -n gitweb
%defattr(-,root,root)
%doc gitweb/INSTALL gitweb/README
%config(noreplace)%{_sysconfdir}/gitweb.conf
%config(noreplace)%{_sysconfdir}/httpd/conf.d/git.conf
%{_var}/www/git/


%files all
# No files for you!

%changelog
* Tue Jun 28 2016 Satoshi Tajima <tajima1989@gmail.com> - 2.9.0-1
- initial build 2.9.0. refs wing-repo.net
