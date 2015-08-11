#!/bin/sh

torsocks wget --recursive --no-clobber --page-requisites --html-extension --convert-links --restrict-file-names=windows --domains eda.ru --no-parent --wait=3 eda.ru
