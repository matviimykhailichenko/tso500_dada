# TSO500 DRAGEN pipeline

_Instructions_:
1. Clone repo;
2. Have conda in your env and install tso500_dragen_pipeline env from `/envs/tso500_dragen_pipeline.yml`
3. Set up crontab.

_Notes_:
- Main code is in file called `snakefile`;
- Test run: 3-4 hours to stage the run + 7 hours to analyse the run + 3-4 hours to transfer results = 15 hours.
- Unified logging. One can find logs in `logs` directory.

_Future features:_
- Validate the samplesheet;
- Conteinerization;
- Make configuration object;
- Check for available storage.

Safety risks:
- Pathlib is deprecated! Change to pathlib2. 

Directives:
- Logging in files is needed to see detailed sequence of operations and notifications are needed to receive quick insight into status and if something breaks