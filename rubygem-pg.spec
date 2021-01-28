%{?scl:%scl_package rubygem-%{gem_name}}
%{!?scl:%global pkg_name %{name}}

# Enable test. This includes RSpec into sources.
%bcond_with tests

# Generated from pg-0.11.0.gem by gem2rpm -*- rpm-spec -*-
%global gem_name pg

Name: %{?scl_prefix}rubygem-%{gem_name}
Version: 1.2.3
Release: 1%{?dist}
Summary: A Ruby interface to the PostgreSQL RDBMS
# Upstream license clarification (https://bitbucket.org/ged/ruby-pg/issue/72/)
#
# The portions of the code that are BSD-licensed are licensed under
# the BSD 3-Clause license; the contents of the BSD file are incorrect.
#
License: (BSD or Ruby) and PostgreSQL
URL: https://github.com/ged/ruby-pg
Source0: https://rubygems.org/gems/%{gem_name}-%{version}.gem
# Sources of RSpec for interanl tests. Don't import these.
%if %{with tests}
Source200: https://rubygems.org/gems/diff-lcs-1.3.gem
Source201: https://rubygems.org/gems/rspec-3.7.0.gem
Source202: https://rubygems.org/gems/rspec-core-3.7.0.gem
Source203: https://rubygems.org/gems/rspec-expectations-3.7.0.gem
Source204: https://rubygems.org/gems/rspec-mocks-3.7.0.gem
Source205: https://rubygems.org/gems/rspec-support-3.7.0.gem
%endif
# Disable RPATH.
# https://bitbucket.org/ged/ruby-pg/issue/183
Patch0: rubygem-pg-0.17.1-remove-rpath.patch
# Required in ext/pg_text_decoder.c
Requires: %{?scl_prefix}rubygem(bigdecimal)
BuildRequires: %{?scl_prefix}ruby(release)
BuildRequires: %{?scl_prefix}rubygems-devel
BuildRequires: %{?scl_prefix}ruby-devel
# Compiler is required for build of gem binary extension.
# https://fedoraproject.org/wiki/Packaging:C_and_C++#BuildRequires_and_Requires
BuildRequires: gcc

BuildRequires: postgresql-server postgresql-devel
BuildRequires: %{?scl_prefix}rubygem(bigdecimal)
Provides: %{?scl_prefix}rubygem(%{gem_name}) = %{version}

%description
This is the extension library to access a PostgreSQL database from Ruby.
This library works with PostgreSQL 9.1 and later.


%package doc
Summary: Documentation for %{pkg_name}
Requires: %{?scl_prefix}%{pkg_name} = %{version}-%{release}
BuildArch: noarch

%description doc
Documentation for %{pkg_name}.

%prep
%{?scl:scl enable %{scl} - << \EOF}
set -ex
gem unpack %{SOURCE0}

%setup -q -D -T -n  %{gem_name}-%{version}

gem spec %{SOURCE0} -l --ruby > ../%{gem_name}-%{version}.gemspec

%patch0 -p1
%{?scl:EOF}

%build
%{?scl:scl enable %{scl} - << \EOF}
set -ex
# Create the gem as gem install only works on a gem file
gem build ../%{gem_name}-%{version}.gemspec

# %%gem_install compiles any C extensions and installs the gem into ./%%gem_dir
# by default, so that we can move it into the buildroot in %%install
%gem_install
%{?scl:EOF}

%install
set -ex
mkdir -p %{buildroot}%{gem_dir}
cp -a .%{gem_dir}/* \
        %{buildroot}%{gem_dir}/

mkdir -p %{buildroot}%{gem_extdir_mri}
cp -a .%{gem_extdir_mri}/{gem.build_complete,*.so} %{buildroot}%{gem_extdir_mri}/

# Prevent dangling symlink in -debuginfo (rhbz#878863).
rm -rf %{buildroot}%{gem_instdir}/ext/

# Remove useless shebangs.
sed -i -e '/^#!\/usr\/bin\/env/d' %{buildroot}%{gem_instdir}/Rakefile
sed -i -e '/^#!\/usr\/bin\/env/d' %{buildroot}%{gem_instdir}/Rakefile.cross

# Files under %%{gem_libdir} are not executable.
for file in `find %{buildroot}%{gem_libdir} -type f -name "*.rb"`; do
    sed -i '/^#!\/usr\/bin\/env/ d' $file \
    && chmod -v 644 $file
done

%if %{with tests}
%check
%{?scl:scl enable %{scl} - << \EOF}
set -ex
pushd .%{gem_instdir}

# Set a test directory to prevent DB start failures due to
# 'Unix-domain socket path "..." is too long (maximum 107 bytes)'.
export RUBY_PG_TEST_DIR="${HOME}/tmp_test_specs"

pushd %{_sourcedir}
gem install rspec*.gem --local --no-document
popd
# Export path with locally installed rspec executable.
export PATH="~/bin:${PATH}"

# Set --verbose to show detail log by $VERBOSE.
# See https://github.com/ged/ruby-pg/blob/master/spec/helpers.rb $VERBOSE
# Assign a random port to consider a case of multi builds in parallel in a host.
# https://github.com/ged/ruby-pg/pull/39
if ! PGPORT="$((54321 + ${RANDOM} % 1000))" ruby -S --verbose \
  rspec -I$(dirs +1)%{gem_extdir_mri} -f d spec; then
  echo "==== [setup.log start ] ===="
  cat tmp_test_specs/setup.log
  echo "==== [setup.log end ] ===="
  false
fi
popd
%{?scl:EOF}
%endif

%files
%dir %{gem_instdir}
%{gem_extdir_mri}
%exclude %{gem_instdir}/.gemtest
%license %{gem_instdir}/BSDL
%license %{gem_instdir}/POSTGRES
%license %{gem_instdir}/LICENSE
%{gem_libdir}
%exclude %{gem_cache}
%{gem_spec}

%files doc
%doc %{gem_docdir}
%doc %{gem_instdir}/ChangeLog
%doc %{gem_instdir}/Contributors.rdoc
%doc %{gem_instdir}/History.rdoc
%doc %{gem_instdir}/Manifest.txt
%doc %{gem_instdir}/README-OS_X.rdoc
%doc %{gem_instdir}/README-Windows.rdoc
%doc %{gem_instdir}/README.ja.rdoc
%doc %{gem_instdir}/README.rdoc
%{gem_instdir}/Rakefile*
%{gem_instdir}/spec

%changelog
* Thu Mar 19 2020 Jun Aruga <jaruga@redhat.com> - 1.2.3-1
- Update to pg 1.2.3.

* Mon Jan 06 2020 Jun Aruga <jaruga@redhat.com> - 1.2.1-1
- Update to pg 1.2.1.
- Add marking lines at the start and end of the setup.log
- Assign a random testing port.

* Thu Jan 10 2019 Vít Ondruch <vondruch@redhat.com> - 1.1.4-1
- Update to pg 1.1.4.

* Sun Feb 18 2018 Jun Aruga <jaruga@redhat.com> - 1.0.0-1
- Update to pg 1.0.0.

* Fri Dec 08 2017 Jun Aruga <jaruga@redhat.com> - 0.21.0-2
- Fix failed tests for PostgreSQL-10.

* Thu Aug 17 2017 Vít Ondruch <vondruch@redhat.com> - 0.21.0-1
- Update to pg 0.21.0.

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.20.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.20.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon May 29 2017 Vít Ondruch <vondruch@redhat.com> - 0.20.0-1
- Update to pg 0.20.0.

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.18.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun Jan 15 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 0.18.4-3
- F-26: rebuild for ruby24
- Patch from the upstream for test failure with integer unification

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.18.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 06 2016 Vít Ondruch <vondruch@redhat.com> - 0.18.4-1
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.3
- Update to pg 0.18.4.

* Wed Aug 26 2015 Vít Ondruch <vondruch@redhat.com> - 0.18.2-1
- Update to pg 0.18.2.

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.18.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Jan 16 2015 Vít Ondruch <vondruch@redhat.com> - 0.18.1-1
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.2
- Update to pg 0.18.1.

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.17.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.17.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Apr 15 2014 Vít Ondruch <vondruch@redhat.com> - 0.17.1-1
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.1
- Update to pg 0.17.1.

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.14.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Mar 07 2013 Vít Ondruch <vondruch@redhat.com> - 0.14.1-1
- Rebuild for https://fedoraproject.org/wiki/Features/Ruby_2.0.0
- Update to pg 0.14.1.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Feb 07 2012 Vít Ondruch <vondruch@redhat.com> - 0.12.2-2
- Obsolete ruby-postgress, which was retired.

* Tue Jan 24 2012 Vít Ondruch <vondruch@redhat.com> - 0.12.2-1
- Rebuilt for Ruby 1.9.3.
- Upgrade to pg 0.12.2.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Jun 03 2011 Vít Ondruch <vondruch@redhat.com> - 0.11.0-5
- Pass CFLAGS to extconf.rb.

* Fri Jun 03 2011 Vít Ondruch <vondruch@redhat.com> - 0.11.0-4
- Binary extension moved into ruby_sitearch dir.
- -doc subpackage made architecture independent.

* Wed Jun 01 2011 Vít Ondruch <vondruch@redhat.com> - 0.11.0-3
- Quoted upstream license clarification.

* Mon May 30 2011 Vít Ondruch <vondruch@redhat.com> - 0.11.0-2
- Removed/fixed shebang in non-executables.
- Removed sources.

* Thu May 26 2011 Vít Ondruch <vondruch@redhat.com> - 0.11.0-1
- Initial package
