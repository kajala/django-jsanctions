django-jsanctions
=================

Parses and imports sanction lists for Django projects. Supports Django 3.0+. Test coverage 69%

Supported sanction lists:
* EU consolidated sanctions list
* OFAC consolidated sanctions list
* UN consolidated sanctions list

Data Sources
============

* http://data.europa.eu/euodp/en/data/dataset/consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions
* https://home.treasury.gov/policy-issues/financial-sanctions/consolidated-sanctions-list-data-files
* https://www.un.org/securitycouncil/content/un-sc-consolidated-list

Install
=======

* pip install django-jsanctions

Unit Tests
==========

* ./test-coverage

Changes
=======

3.6.0:
+ Added OFAC and UN list import

3.5.0:
+ Refactoring

3.0.0:
+ Django 3.0 support
