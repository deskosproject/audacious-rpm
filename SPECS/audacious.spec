# Minimum audacious/audacious-plugins version in inter-package dependencies.
%global aud_ver 3.5

%global tar_ver 3.5.1

# Audacious Generic Plugin API defined in audacious-libs subpackage.


Name: audacious
Version: 3.5.1
Release: 1%{?dist}

License: BSD
Summary: Advanced audio player
URL: http://audacious-media-player.org/
Group: Applications/Multimedia

Source0: http://distfiles.audacious-media-player.org/audacious-%{tar_ver}.tar.bz2
# validated: 2013-11-03 / screenshot commented out for now
Source1: audacious.appdata.xml

BuildRequires: gettext
BuildRequires: gtk3-devel
BuildRequires: libguess-devel
BuildRequires: dbus-devel
BuildRequires: dbus-glib-devel
BuildRequires: desktop-file-utils

# The automatic SONAME dependency is not enough
# during version upgrades.
Requires: audacious-libs%{?_isa} = %{version}-%{release}

# For compatibility with the plugin API implemented by the player,
# a minimum version of the base plugins package is strictly required.
Requires: audacious-plugins%{?_isa} >= %{aud_ver}

# Audacious stores its own icon(s) in the hicolor tree
# and updates the icon cache.
Requires: hicolor-icon-theme

# Skin packages can require this from xmms and all GUI compatible players
Provides: xmms-gui

%description
Audacious is an advanced audio player. It is free, lightweight, currently
based on GTK+ 3, runs on Linux and many other *nix platforms and is
focused on audio quality and supporting a wide range of audio codecs.
It still features an alternative skinned user interface (based on
Winamp 2.x skins). Historically, it started as a fork of Beep Media
Player (BMP), which itself forked from XMMS.


%package libs
Summary: Library files for the Audacious audio player
Group: System Environment/Libraries
# Provide Generic Plugin API value for plugin packages to depend on.
# As defined in /usr/include/audacious/plugin.h: _AUD_PLUGIN_VERSION
# This must be an exact match for plugin .so files to load.
# If multiple versions are supported, add multiple Provides below.
%global aud_plugin_api 45
%global aud_plugin_api_min 45
Provides: audacious(plugin-api)%{?_isa} = %{aud_plugin_api}
#Provides: audacious(plugin-api)%{?_isa} = 45
#Provides: audacious(plugin-api)%{?_isa} = %{aud_plugin_api_min}

%description libs
Library files for the Audacious audio player.


%package devel
Summary: Development files for the Audacious audio player
Group: Development/Libraries
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: glib2-devel%{?_isa}
Requires: gtk3-devel%{?_isa}
Requires: dbus-glib-devel%{?_isa}
# added on 2014-02-23 (F21 development)
Obsoletes: %{name}-doc < 3.5

%description devel
Files needed when building software for the Audacious audio player.


%prep
%setup -q -n %{name}-%{tar_ver}

# Verify the value of the audacious(plugin-api) Provides.
api=$(grep '[ ]*#define[ ]*_AUD_PLUGIN_VERSION[ ]\+' src/audacious/api.h | sed 's!.*_AUD_PLUGIN_VERSION[ ]*\([0-9]\+\).*!\1!')
[ "${api}" == "%{aud_plugin_api}" ] || exit -1
api_min=$(grep '[ ]*#define[ ]*_AUD_PLUGIN_VERSION_MIN' src/audacious/api.h | sed 's!.*_AUD_PLUGIN_VERSION_MIN[ ]*\([0-9]\+\).*!\1!')
[ "${api_min}" == "%{aud_plugin_api_min}" ] || exit -1

sed -i '\,^.SILENT:,d' buildsys.mk.in


%build
%configure  \
    --with-buildstamp="Fedora package"  \
    --disable-rpath \
    --disable-dependency-tracking
make %{?_smp_mflags}


%install
make install DESTDIR=${RPM_BUILD_ROOT} INSTALL="install -p"
find ${RPM_BUILD_ROOT} -type f -name "*.la" -exec rm -f {} ';'

%find_lang %{name}

desktop-file-install  \
    --dir ${RPM_BUILD_ROOT}%{_datadir}/applications  \
    ${RPM_BUILD_ROOT}%{_datadir}/applications/audacious.desktop

install -D -m0644 %{SOURCE1} ${RPM_BUILD_ROOT}%{_datadir}/appdata/%{name}.appdata.xml


%post
/usr/bin/update-desktop-database &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
/usr/bin/update-desktop-database &> /dev/null || :

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files -f %{name}.lang
%doc AUTHORS
%{_bindir}/audacious
%{_bindir}/audtool
%{_datadir}/audacious/
%{_mandir}/man[^3]/*
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}*.*
%{_datadir}/appdata/%{name}.appdata.xml

%files libs
# license file included in this subpkg
# for Fedora Licensing Guidelines change (2010-07-07)
%doc COPYING
%{_libdir}/*.so.*

%files devel
%{_includedir}/audacious/
%{_includedir}/libaudcore/
%{_includedir}/libaudgui/
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc


%changelog
* Thu Jul 24 2014 Michael Schwendt <mschwendt@fedoraproject.org> - 3.5.1-1
- Update to 3.5.1.

* Tue Jun 24 2014 Michael Schwendt <mschwendt@fedoraproject.org> - 3.5-3
- Drop the old non-arch-specific Plugin API version capabilities.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Apr 23 2014 Michael Schwendt <mschwendt@fedoraproject.org> - 3.5-1
- Update to 3.5 final release.
- Merge spec changes from packages released via Fedora Copr:
  - Obsolete -doc subpackage.
  - Disable Doxygen temporarily (missing 'doc' dir) build dummy -doc package.
  - Plugin version moved to api.h header.
  - Generic plugin API/ABI bumped to 45, with 45 also being the minimum.

* Wed Jan  8 2014 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4.3-1
- Update to 3.4.3 (a few bug-fixes and translation updates).

* Sun Nov  3 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4.2-2
- Create and install a preliminary AppData file (for upstream #349).

* Sun Nov  3 2013 Dan Fruehauf <malkodan@gmail.com> - 3.4.2-1
- Update to 3.4.2 final (fixes bugs 340, 346, 347, 356, 360, and 362).

* Fri Sep 13 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4.1-2
- Merge fix for upstream bug 340: When probing file content, immediately
  reject out-of-bounds seek requests.

* Mon Sep  9 2013 Dan Fruehauf <malkodan@gmail.com> - 3.4.1-1
- Update to 3.4.1 final (a few bug fixes).

* Sat Aug 31 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4-4
- Merge fix for upstream bug 332: Increase maximum file-probing buffer
  to 256 KB to handle Vorbis files that put high-res album art before
  the audio stream.

* Mon Aug 26 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4-3
- Add absolute paths to commands in scriptlets.
- Move developer HTML documentation into new noarch audacious-doc
  subpackage.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Jun 29 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4-1
- Update to 3.4 final (a few bug-fixes and translation updates).

* Wed Jun 12 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4-0.4.beta2
- Update to 3.4-beta2 (which also includes newer Autotools files).

* Mon May 13 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4-0.3.beta1
- Merge upstream fix for incorrect parsing of ID3 "TIME" field.

* Thu Apr 25 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4-0.2.beta1
- Apply patch to restore play-stop-play resume from beginning behaviour.

* Mon Apr 22 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4-0.1.beta1
- Generic plugin API/ABI bumped to 43, still compatible with 3.3.x.
- Update to 3.4-beta1.
- BR autoconf automake gettext-devel and
  run autoreconf -f -I m4 for aarch64 updates (#925050).

* Thu Feb  7 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.4-0.1.alpha1
- Generic plugin API/ABI bumped to 42, still compatible with 3.3.x.
- Incremental upgrade to 3.4-alpha1.
- Use %%_isa also for deps on -devel packages.

* Sun Feb  3 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.3.4-1
- Update to 3.3.4 (last upstream maintenance release for 3.3.x).

* Fri Jan 11 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 3.3.3-2
- Keep all MimeType definitions in the single .desktop file, even if the
  corresponding plug-ins may be missing. This is supposed to fix the
  assignment of Default Applications (GNOME bz #690119).

* Tue Dec 11 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.3.3-1
- Update to 3.3.3 (a few bug-fixes and translation updates).

* Mon Sep 24 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.3.2-1
- Update to 3.3.2 (a few bug-fixes and translation updates).
- Merge content detection fix for URLs that contain parameters.

* Mon Aug 13 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.3.1-1
- Update to 3.3.1 (a few bug-fixes and translation updates).

* Fri Jul 27 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.3-1
- Update to 3.3 final.

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3-0.2.beta2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul 16 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.3-0.1.beta2
- Generic plugin API/ABI bumped to 41, with 40 being the minimum.
- Update to 3.3-beta2.

* Thu Jul  5 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.3-0.1.beta1
- License of this package has changed to two-clause BSD.
- Update to 3.3-beta1.

* Mon Jun 18 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.3-0.1.alpha1
- Generic plugin API/ABI bumped to 40, also the minimum.
- Adjust files section for dropped files.
- Upgrade to 3.3-alpha1.

* Sat May 26 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.2.3-1
- Update to 3.2.3 (bug-fixes and translation updates).

* Sun Apr  1 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.2.2-1
- Update to 3.2.2 (extensive symbol collision fixes/prevention and
  translation updates).

* Sat Feb 18 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.2.1-1
- Update to 3.2.1 (first bugfix release in 3.2.x branch).

* Sat Jan 21 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.2-1
- Update to 3.2 final (mostly translation updates and a very few fixes).

* Thu Jan 12 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.2-0.5.beta2
- Update to 3.2-beta2.

* Sun Jan  8 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.2-0.4.beta1
- With libmowgli not being used anymore, also remove the explicit dep.

* Mon Jan  2 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.2-0.3.beta1
- Remove undefined @PC_REQUIRES@ in audclient.pc file.

* Mon Jan  2 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 3.2-0.2.beta1
- Generic plugin API/ABI bumped to 38, also the minimum.
- Update to 3.2-beta1.

* Fri Dec 23 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.2-0.1.alpha1
- Explicitly link with gmodule-2.0.pc libs for missing libs.
- Generic plugin API/ABI bumped to 37, also the minimum.
- libmowgli not used anymore.
- Upgrade to 3.2-alpha1.

* Tue Dec  6 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.1.1-1
- Update to 3.1.1.

* Wed Nov  9 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.1-1
- Update to 3.1.

* Wed Oct 26 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.1-0.1.beta3
- Generic plugin API/ABI bumped to 34, also the minimum.
- Update to 3.1-beta3.

* Mon Oct 17 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.1-0.1.beta2
- Update to 3.1-beta2.

* Tue Oct 11 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.1-0.1.beta1
- Generic plugin API/ABI bumped to 33, also the minimum.
- Update to 3.1-beta1.

* Wed Sep 21 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.1-0.1.alpha1
- Generic plugin API/ABI bumped to 32, with 31 being the minimum.
- libmcs not used anymore.
- Upgrade to 3.1-alpha1.

* Mon Sep 19 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.0.3-1
- Update to 3.0.3 (just a few spelling fixes and translation updates).

* Sat Sep 17 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.0.2-3
- Add audacious(plugin-api)%%{?_isa} Provides which plugin packages
  may use for an arch-specific dependency (albeit not before builds of
  this base package become available for the target dist).

* Fri Sep 16 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.0.2-2
- Use %%_isa in more dependencies.
- Drop unneeded BuildRoot stuff.
- Drop %%defattr lines.
- Drop explicit pkgconfig dependency.

* Thu Aug 25 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.0.2-1
- Update to 3.0.2 (just a few fixes plus translation updates).

* Thu Aug 11 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.0.1-1
- Update to 3.0.1 (just a few fixes plus translation updates).

* Tue Jul 19 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.0-1
- Update to 3.0 release.

* Mon Jul  4 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.0-0.3.beta1
- Generic plugin API/ABI minimum version bumped to 31.
- Update to 3.0-beta1.

* Wed Jun 22 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.0-0.2.alpha1
- Move audacious(plugin-api) Provides to the audacious-libs package.

* Tue Jun 14 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 3.0-0.1.alpha1
- Build with GTK+ 3.
- Generic plugin API/ABI minimum version bumped to 30.
- Upgrade to 3.0-alpha1.

* Thu May 19 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.5.1-1
- Update to 2.5.1.

* Sat Apr 23 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.5.0-3
- Merge fix for skinned ui track next/prev (AUD-331).

* Fri Apr 22 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.5.0-2
- Only --disable-sse2 for %%ix86.

* Sat Apr 16 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.5.0-1
- Update to 2.5.0.

* Thu Apr  7 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.5-0.5.beta2
- Don't forget "audacious(plugin-api) = 19".

* Wed Apr  6 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.5-0.4.beta2
- Update to 2.5-beta2.
- Generic plugin API/ABI bumped to 20, with 18 being the minimum.

* Sat Mar 26 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.5-0.3.beta1
- Sync desktop file modifications with the 2.4.4 packages and the
  current state in 2.5-beta1.
- Remove audio/midi MIME type from desktop file, because it is only
  supported with the optional audacious-plugins-amidi package.

* Thu Mar 10 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.5-0.2.beta1
- Update to 2.5-beta1.

* Tue Feb 22 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.5-0.1.alpha2
- Upgrade to 2.5-alpha2.
- Generic plugin API/ABI bumped to 19, with 18 still supported.

* Mon Jan 31 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.5-0.1.alpha1
- Upgrade to 2.5-alpha1.
- Generic plugin API/ABI bumped to 18.
- Plugin API define has changed from __AUDACIOUS_PLUGIN_API__ to
  _AUD_PLUGIN_VERSION
- .desktop files got renamed!
- executables got renamed!
- BR doxygen and include HTML documentation in -devel package

* Fri Jan 28 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4.3-4
- Merge fixes for AUD-285, AUD-286.

* Thu Jan 27 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4.3-3
- Provide versioned capability audacious(plugin-api) as something much more
  specific for plugin packages to require.

* Fri Jan 14 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4.3-1
- Update to 2.4.3 (maintenance release in stable branch, 18k diff).

* Thu Dec  9 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4.2-1
- Update to 2.4.2 (maintenance release in stable branch).
- Generic plugin API/ABI bumped to 17.
- Remove NEWS file not updated since 2.1.0.

* Sat Nov  6 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4.0-5
- libaudcore: vfs_file_get_contents should set returned values 
  to NULL and 0 on failure.

* Wed Sep 29 2010 jkeating - 2.4.0-4
- Rebuilt for gcc bug 634757

* Tue Sep 14 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4.0-3
- Replace file-ext-in-url patch with upstream's probe.c commit.
- Enable gnomeshortcuts plugin by default, if not disabled in
  user's preferences (#632388).

* Mon Sep 13 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4.0-2
- Strip off parameters of HTTP/HTTPS URLs to fix file name extension
  detection (#632367, Hans de Goede).

* Thu Aug 26 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4.0-1
- Update to 2.4.0 final.
- Update spec file comments, summary, description, also because
  the skinned user-interface no longer is the default.

* Sat Aug 14 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.10.rc2
- Update to rc2.

* Fri Aug 13 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.10.rc1
- Fix album art loader to convert file:// URIs into filenames.

* Tue Aug 10 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.9.rc1
- Update to rc1.

* Tue Aug  3 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.8.beta2
- Update to beta2.

* Fri Jul 23 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.7.beta1
- At least audacious-plugins-2.4-0.5.beta1 is needed for this.

* Wed Jul 21 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.6.beta1
- Generic plugin API/ABI bumped to 16.
- Update to beta1.

* Mon Jul 12 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.5.alpha3
- Generic plugin API/ABI bumped to 15.
- .desktop files got renamed!
- BR libguess-devel (split off after alpha2)
- Update to alpha3.

* Thu Jul  8 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.4.alpha2
- Include license file also in the -libs subpackage
  for Fedora Licensing Guidelines change (2010-07-07).

* Tue Jun 29 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.3.alpha2
- Update scriptlets for hicolor icon maintenance.
- Update to alpha2.

* Sat Jun 12 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.2.alpha1
- Use --with-buildstamp.

* Wed Jun  9 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.4-0.1.alpha1
- Drop obsolete BR libsamplerate-devel and --enable-samplerate.
- Upgrade to 2.4 alpha1.

* Wed Jun  9 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-16
- Enhance the coverart patch to not crash in URI conversion (#602113).

* Fri Apr 16 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-15
- Fix manual and --help for options -e/-E (#581394 and AUD-174).

* Sat Mar 20 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-14
- Unescape filename uri in fileinfo dialog to avoid g_markup crash (#575387).

* Sat Mar  6 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-13
- Enhance the coverart patch to not display an empty filename for
  streams when title isn't known yet and filename isn't either.

* Mon Feb 15 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-12
- Fix album cover art image loader (which cannot handle vfs URIs).

* Sat Feb 13 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-11
- Explicitly link with libm because of:
  http://fedoraproject.org/wiki/Features/ChangeInImplicitDSOLinking

* Thu Jan 28 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-10
- Fix tuple_copy() further (it was completely broken as the mowgli
  dict wasn't copied at all).

* Thu Jan 28 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-9
- Let set_tuple_cb() work on a copied tuple
  (the metadata updates flood is too racy IMO).
- Fix tuple_copy().

* Wed Jan 27 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-8
- Change build_stamp from "UNSUPPORTED VERSION" to "Fedora package".
- Always add category AudioVideo to .desktop file for safety reasons.

* Sat Jan 23 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-7
- Patch filename_find_decoder to probe a file if multiple decoders
  compete with eachother to handle files with the same extension.
  This also merges the 2nd chunk of the disabled-iplugins patch.

* Sun Jan 17 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-6
- In audacious.pc link with -laudcore instead of -laudclient (AUD-125).
  This removes a superfluous libaudclient dependency from all plugins and
  adds a libaudcore dependency. So far, plugins that use libaudcore
  had undefined symbols instead.

* Thu Jan  7 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-5
- Apply fix for seeking to -1 milliseconds, causing a hangup (AUD-99).

* Thu Dec 31 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-4
- Added another fix to the disabled-iplugins patch.

* Wed Dec 30 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-3
- Patch Audacious so that filename_find_decoder only considers
  enabled input plugins (disabled modplug plugin effectively disabled
  also the xmp plugin).

* Wed Dec  2 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-2
- Drop Musepack and SID MIME types from desktop files. As of Audacious 2.2,
  Musepack is only supported by the separate "ffaudio" plugin. The SID
  plugin in a separate subpackage provides its own desktop file.
- Drop unsupported MIME types from desktop files.

* Wed Nov 25 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-1
- Upgrade to 2.2 (declared as the next "stable release" after 2.1).

* Tue Nov 10 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-0.1.beta2
- Upgrade to 2.2-beta2

* Thu Oct 22 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-0.1.beta1
- Upgrade to 2.2-beta1

* Sun Oct 18 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-0.1.alpha2
- Upgrade to 2.2-alpha2

* Sun Sep 20 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.2-0.1.alpha1
- Upgrade to 2.2-alpha1 (primarly for alsa-gapless output plugin).
- /usr/bin/audacious and /usr/bin/audtool compatibility links are now
  provided officially by upstream.

* Sun Sep 20 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.1-5
- /usr/bin/audacious and /usr/bin/audtool compatibility links are
  provided officially by upstream within 2.2-alpha1.

* Sat Sep 12 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.1-4
- Build with --enable-samplerate (off by default), BR libsamplerate-devel

* Mon Aug 24 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.1-3
- Default to PulseAudio output plugin: Fix pluginenum.c indentation
  to make output plugin default/priority init work. Actually, when I
  noticed this bug, I went a step further and copied a rewrite from
  upstream devel scm.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.1-1
- Upgrade to 2.1 final.

* Mon Jun 29 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.1-0.1.beta1
- Upgrade to 2.1beta1.
- Drop obsolete patches.

* Fri Jun  5 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.0.1-0.1
- Initial package for Audacious 2.0.1
  based on a major spec overhaul of the older Fedora packages.