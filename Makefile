#!/usr/bin/make -f
# Makefile for Cadence #
# ---------------------- #
# Created by falkTX
#

PREFIX  = /usr/local
DESTDIR =
RESDIR := ./resources

LINK   = ln -s
PYUIC ?= pyuic5
PYRCC ?= pyrcc5

I18N_LANGUAGES :=
TSs = $(patsubst %,src/translations/catia_%.ts,$(I18N_LANGUAGES))
QMs = $(patsubst %,src/translations/catia_%.qm,$(I18N_LANGUAGES))

# -----------------------------------------------------------------------------------------------------------------------------------------

all: RES UI $(QMs)

# -----------------------------------------------------------------------------------------------------------------------------------------
# Resources

RES: src/resources_rc.py

src/resources_rc.py: resources/resources.qrc
	$(PYRCC) $< -o $@

# -----------------------------------------------------------------------------------------------------------------------------------------
# UI code

UI: src/ui_catia.py src/ui_settings_app.py

src/ui_%.py: resources/ui/%.ui
	$(PYUIC) $< -o $@

# -----------------------------------------------------------------------------------------------------------------------------------------

clean:
	rm -f *~ src/*~ src/*.pyc src/ui_*.py src/resources_rc.py $(QMs)

# -----------------------------------------------------------------------------------------------------------------------------------------

debug:
	$(MAKE) DEBUG=true

# -----------------------------------------------------------------------------------------------------------------------------------------

install:
	# Create directories
	install -d $(DESTDIR)$(PREFIX)/bin
	install -d $(DESTDIR)$(PREFIX)/share/applications
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/16x16/apps
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/48x48/apps
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/128x128/apps
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/256x256/apps
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps
	install -d $(DESTDIR)$(PREFIX)/share/catia/jacklib
	install -d $(DESTDIR)$(PREFIX)/share/catia/patchcanvas
	install -d $(DESTDIR)$(PREFIX)/share/catia/translations

	# Install script files and binaries
	install -m 755 \
		data/catia \
		$(DESTDIR)$(PREFIX)/bin/

	# Install desktop files
	install -m 644 data/*.desktop           $(DESTDIR)$(PREFIX)/share/applications/

	# Install icons
	install -m 644 resources/16x16/catia.png    $(DESTDIR)$(PREFIX)/share/icons/hicolor/16x16/apps/
	install -m 644 resources/48x48/catia.png    $(DESTDIR)$(PREFIX)/share/icons/hicolor/48x48/apps/
	install -m 644 resources/128x128/catia.png  $(DESTDIR)$(PREFIX)/share/icons/hicolor/128x128/apps/
	install -m 644 resources/256x256/catia.png  $(DESTDIR)$(PREFIX)/share/icons/hicolor/256x256/apps/
	install -m 644 resources/scalable/catia.svg $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/

	# Install main code
	install -m 755 src/*.py             $(DESTDIR)$(PREFIX)/share/catia/
	install -m 755 src/jacklib/*.py     $(DESTDIR)$(PREFIX)/share/catia/jacklib/
	install -m 755 src/patchcanvas/*.py $(DESTDIR)$(PREFIX)/share/catia/patchcanvas/

	# Adjust PREFIX value in script files
	sed -i "s?X-PREFIX-X?$(PREFIX)?" \
		$(DESTDIR)$(PREFIX)/bin/catia \

	# Install translations
	$(foreach l,$(I18N_LANGUAGES),install -m 644 \
		src/translations/catia_$(l).qm \
		$(DESTDIR)$(PREFIX)/share/catia/translations/;)

# -----------------------------------------------------------------------------------------------------------------------------------------

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/catia
	rm -f $(DESTDIR)$(PREFIX)/share/applications/catia.desktop
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/*/apps/catia.png
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/catia.svg
	rm -rf $(DESTDIR)$(PREFIX)/share/catia

i18n_update: $(TSs)
i18n_release: $(QMs)

src/translations/%.ts:
	@install -d src/translations
	pylupdate5 src/*.py $(RESDIR)/ui/*.ui -ts $@

%.qm: %.ts
	lrelease $< -qm $@
