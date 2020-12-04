History
=======

0.2.4.imio2 (unreleased)
------------------------

- Nothing changed yet.


0.2.4 (2020-12-04)
------------------

* Quickfix: Always try to parse JSON (as default) from response
  Youtube stopped sending correct Content-Type header: text/html instead of JSON
  [laulaz]

* Add timeout
  Give the possibility to add a urllib timeout for a OEmbedEndpoint
  [jfroche]

* support non-standard text/javascript response
  [sk1p, abarmat]

* Fix packaging por pypi

0.2.3 (2015-04-02)
------------------

* Add Python 3 compatibility

0.2.2 (2012-06-08)
------------------

* If the endpoint URL already had URL parameters, use an ampersand instead to append URL parameters.

0.2.1 (2011-12-29)
------------------

* Fix build problems in setup.py

0.2.0 (2011-10-20)
------------------

* Update code format
* Improve import selection of JSON and XML libraries
* Remove unused files

0.1.2 (2009-07-28)
------------------

* Bugfix: resolved issue #1
* Added test case to the URL matching

0.1.1 (2008-09-08)
------------------

* Fixed mime-type check. It failed when more tokens where present in the content-type.
* Added new mime-type "application/xml".
* Changed minor error on package descriptor.

0.1.0 (2008-09-05)
------------------

* First release
