all: pylint check

# LINTERS AND STATIC CHECKERS
pylint:
	pylint slowbeast/

fixme:
	pylint --enable=fixme slowbeast/

# FORMATTING
black:
	black slowbeast/

autopep:
	autopep8 --in-place --aggressive --aggressive --recursive slowbeast


# TESTING
check:
	lit -j4 --path=$(shell pwd) -D OPTS="-se-step=block" tests/
	lit -j4 --path=$(shell pwd) -D OPTS="-se -bse" tests/
	lit -j4 --path=$(shell pwd) -D OPTS="-se -bself" tests/
	lit -j4 --path=$(shell pwd) -D OPTS="-se -kindse" tests/

check-bse:
	lit -j4 --path=$(shell pwd) -v -D OPTS="-bse" tests/

check-bself:
	lit -j4 --path=$(shell pwd) -a -D OPTS="-bself" tests/

check-kindse:
	lit -j4 --path=$(shell pwd) -a -D OPTS="-kindse" tests/

check-all:
	lit -j4 --path=$(shell pwd) -D OPTS="-se-step=instr" tests/
	lit -j4 --path=$(shell pwd) -D OPTS="-se-step=block" tests/
	lit -j4 --path=$(shell pwd) -D OPTS="-se-incremental-solving" tests/
	lit -j4 --path=$(shell pwd) -D OPTS="-se -kind" tests/
	lit -j4 --path=$(shell pwd) -D OPTS="-se -kind -kind-naive" tests/
	lit -j4 --path=$(shell pwd) -D OPTS="-se -bse" tests/
	lit -j4 --path=$(shell pwd) -D OPTS="-se -bself" tests/
	lit -j4 --path=$(shell pwd) -D OPTS="-se -kindse" tests/

check-v:
	lit -j4 --path=$(shell pwd) -a -D tests/
	lit -j4 --path=$(shell pwd) -a -D OPTS="-bself" tests/
	lit -j4 --path=$(shell pwd) -a -D OPTS="-kindse" tests/

.PHONY: all pylint black autopep check check-bself check-all check-v
