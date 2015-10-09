platform=$(shell uname -s)
conda_path=$(shell which conda)

.PHONY: show check-env venv check run

ifeq ($(platform),Darwin)

ifneq ($(findstring conda,$(conda_path)),conda)
	$(error Conda not present)
else
	@echo Conda present at $(conda_path)
endif

ifeq ($(SUMMARIZE_VENV),)
SUMMARIZE_VENV=summarize_venv
endif
ifeq ($(CONDA_ENV_PATH),)
CONDA_ENV_PATH=//anaconda
endif

PYLIBS := numpy scipy scikit-learn gensim
VENVDIR := $(CONDA_ENV_PATH)/envs/$(SUMMARIZE_VENV)

$(VENVDIR):
	test -d $(VENVDIR) || conda create -y -n $(SUMMARIZE_VENV) $(PYLIBS)

deps: $(VENVDIR)

check: $(VENVDIR)
	source activate $(SUMMARIZE_VENV);\
	python ./test_summarizer.py

run: $(VENVDIR)
	source activate $(SUMMARIZE_VENV);\
	python ./ts_summarizer.py

else ifeq ($(platform),Linux)

VENVDIR := ./venv
PYVENV := $(VENVDIR)/bin/python
NBVENV := $(VENVDIR)/bin/ipython
PIPVENV := $(VENVDIR)/bin/pip

clean:
	rm -r $(VENVDIR)

check: | $(VENVDIR)
	$(PYVENV) ./test_summarizer.py

$(VENVDIR):
	test -d $(VENVDIR) || (virtualenv $(VENVDIR);\
	$(PIPVENV) install -r ./requirements.txt)

else
	$(error, Unknown platform)

endif
