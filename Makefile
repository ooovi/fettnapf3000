start:
	cd src && python server.py 8000

extract-messages:
	xgettext -o src/locales/fettnapf.pot src/*.py src/pages/*.py
	msgmerge --lang=de  --update src/locales/de/LC_MESSAGES/fettnapf.po src/locales/fettnapf.pot
	msgmerge --lang=en --update src/locales/en/LC_MESSAGES/fettnapf.po src/locales/fettnapf.pot

compile-messages:
	msgfmt -o src/locales/en/LC_MESSAGES/fettnapf.mo src/locales/en/LC_MESSAGES/fettnapf.po
	msgfmt -o src/locales/de/LC_MESSAGES/fettnapf.mo src/locales/de/LC_MESSAGES/fettnapf.po