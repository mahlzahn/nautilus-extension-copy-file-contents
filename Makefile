PREFIX ?= $(HOME)/.local
INSTALL_PATH = $(DESTDIR)$(PREFIX)/share/nautilus-python/extensions
MODULES_NAME = nautilus_copy_file_contents

all: pycache

install:   $(patsubst $(MODULES_NAME).py,install-%,  $(notdir $(wildcard src/$(MODULES_NAME).py)))
uninstall: $(patsubst $(MODULES_NAME).py,uninstall-%,$(notdir $(wildcard $(INSTALL_PATH)/$(MODULES_NAME).py)))

pycache:
	python -m compileall src

clean:
	rm -rf src/__pycache__

install-%:
	install -dm755 $(INSTALL_PATH)/__pycache__
	install -m755 src/$(MODULES_NAME).py $(INSTALL_PATH)
	test -f src/__pycache__/$(MODULES_NAME).*.pyc && install -m755 src/__pycache__/$(MODULES_NAME).*.pyc $(INSTALL_PATH)/__pycache__ || true

uninstall-%:
	rm -f $(INSTALL_PATH)/$(MODULES_NAME).py
	rm -f $(INSTALL_PATH)/__pycache__/$(MODULES_NAME).*.pyc
	rmdir -p --ignore-fail-on-non-empty $(INSTALL_PATH)/__pycache__
