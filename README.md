# TSO500 DRAGEN pipeline

_Instructions_:
1. clone repo;
2. have conda in your env and install tso500_dragen_pipeline env from `/envs/tso500_dragen_pipeline.yml`
3. set up crontab.

_Notes_:
- main code is in file called `snakefile`;
- test run: 3-4 hours to stage the run + 7 hours to analyse the run + 3-4 hours to transfer results = 15 hours.
- unified logging. One can find logs in `logs` directory;
- exceptions will stop the pipeline, but if raised specifically (not in try statements).

_Future features:_
- validate the samplesheet;
- conteinerization;
- make configuration object;
- check for available storage;
- testing with pytest.

Safety risks:
- pathlib is deprecated! Change to pathlib2. 

Directives:
- logging in files is needed to see detailed sequence of operations and notifications are needed to receive quick insight into status and if something breaks