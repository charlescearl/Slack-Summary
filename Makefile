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
SUMMARIZE_VENV=summarize_venv2
endif
ifeq ($(CONDA_ENV_PATH),)
CONDA_ENV_PATH=//anaconda
endif

HOST_IP?=10.0.0.10
NB_PORT?=8887
PYLIBS := numpy scipy scikit-learn gensim spacy flask
VENVDIR := $(CONDA_ENV_PATH)/envs/$(SUMMARIZE_VENV)

$(VENVDIR):
	test -d $(VENVDIR) || conda create -y -n $(SUMMARIZE_VENV) $(PYLIBS)

deps: $(VENVDIR)

check: $(VENVDIR)
	source activate $(SUMMARIZE_VENV);\
	python ./test_summarizer.py;\
	python ./test_service_components.py

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
	$(PYVENV) ./test_summarizer.py;\
	$(PYVENV) ./test_service_components.py

run: | $(VENVDIR)
	$(PYVENV) ./ts_summarizer.py

notebook: | $(VENVDIR)
	$(NBVENV) notebook --ip=$(HOST_IP) --port=$(NB_PORT) --no-browser

$(VENVDIR):
	test -d $(VENVDIR) || (virtualenv $(VENVDIR);\
	$(PIPVENV) install -r ./requirements.txt;\
	$(PYVENV) -m spacy.en.download all)

else
	$(error, Unknown platform)

endif
