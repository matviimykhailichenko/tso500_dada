# TSO500 DRAGEN pipeline

_Instructions_:
1. clone repo;
2. have conda in your env and install tso500_dragen_pipeline env from `/envs/tso500_dragen_pipeline.yml`;
3. set up crontab.

_Notes_:
- main code is in file called `snakefile`;
- test run: 3 hours to stage the run + 7 hours to analyse the run + 3-4 hours to transfer results = 15 hours.
- unified logging. One can find logs in `logs` directory;
- exceptions will stop the pipeline, but if raised specifically (not in try statements);
- it won't log/notify bot if the script it tries to run does now exist 

_Future features:_
- deleting temporary log files if run had failed and putting failed tag;
- validate the samplesheet;
- conteinerization;
- make a configuration object;
- check for available storage;
- testing with pytest;
- not deal with temporary logs;
- search for the tso500 script

Safety risks:
- pathlib is deprecated! Change to pathlib2. 

Directives:
- logging in files is needed to see detailed sequence of operations and notifications are needed to receive quick insight into status and if something breaks;
- variables are named like this {structure name}_{structure type}_{data type}


If something breaks, reach matvii.mykhailichenko@medunigraz.at.