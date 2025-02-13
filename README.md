# TSO500 DRAGEN pipeline

_Instructions_:
1. Clone repo;
2. Have conda in your env and install tso500_dragen_pipeline env from `/envs/tso500_dragen_pipeline.yml`;
3. Instal

_Notes_:
- Main code is in file called `snakefile`;
- Stuff that is commented out will be run on the server, stuff that is written now is intended to run locally.
- Decided to go with server availability to not search through archive twice;
- Takes 7 hours to analyse the test run.

_Current features:_
1. Unified logging. One can find logs in `logs` directory.


TODO: 
- Logging. As these occurrences write to the TSO bot: error, exception  or run status

_Future features:_
- Validate the samplesheet;
- Conteinerization.

Safety risks:
- Pathlib is deprecated! Change to pathlib2. 

Notes:
