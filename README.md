# TSO500 DRAGEN pipeline

_Instructions_:
1. Clone repo;
2. Have conda in your env and install tso500_dragen_pipeline env from `/envs/dev/tso500_dragen_pipeline.yml`;
3. Run with `snakemake -j1`.

_Notes_:
1. Main code is in file called `snakefile`;
2. Stuff that is commented out will be run on the server, stuff that is written now is intended to run locally.

_Current features:_
1. Unified logging. One can find logs in `logs` directory.

_Future features:_
- Oncoservise prioretisation. After each run analysis check if there is an Oncoservice run.
- Validate the samplesheet