# TSO500offtarget_ichorCNA

## Contributors
original work by Gavin Ha (Victor Adalsteinsson Lab)
Adapted initially by Isaac Lazzeri
Adapted further for off-target read-based ichorCNA analysis by Raul Alejandro Mejia Pedroza
Adapted for parallel processing of samples using multiprocessing for duplicate marking on a SLURM HPC environment by Bejamin Gernot Spiegl

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://git.medunigraz.at/o_spiegl/tso500offtarget_ichorcna.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://git.medunigraz.at/o_spiegl/tso500offtarget_ichorcna/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Automatically merge when pipeline succeeds](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing(SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***


## Suggestions for a good README
Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
TSO500 off-target ichorCNA
(tso500offtarget_ichorcna)

## Description
This repository contains code to run ichorCNA on off-target reads from aligned Illumina TSO500 ctDNA paired-end 
read data (reads created with a cfDNA enrichment protocol).

## Installation
Clone the repo:

`git clone https://git.medunigraz.at/o_spiegl/tso500offtarget_ichorcna.git`

(you might need to change to the dev branch if the repo is still under development: `git checkout dev`)

This piece of software requires the creation of the conda environment from the YAML file in ./conda/TSO500ichorCNA.yml 
and a repo clone of ichorCNA GitHub repository.

`conda env create -f ./conda/TSO500ichorCNA.yml`

The latter can be created with:

`git clone https://github.com/broadinstitute/ichorCNA.git`

# Performance
The duration of single-sample job execution (24 logical cores) was between 25 minutes and 37 minutes for samples of Oncoservice run '250611_TSO500_Onco' (6.6-9.9 GB BAMs), using 24 cores and up to 120 GB per job.
(reduced the RAM requirements to 2 GB per parallel process based on the total amount of memory used as stated by slurm)

On the MedBioNode HPC cluster of Medical University of Graz, a test with 8 TSO500 liquid samples revealed that with high cluster usage, 1h 15 minutes timespan was between the first sample analysis start and the lsat sample analysis start.

The initial waiting time with 600 jobs in the queue was between 30 minutes and 1 hour. Node reservation requested.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

This pipeline was created and tested only with conda version 23.1.0 and 23.11.0 on a Centos8 system:
 - samtools --version: 1.22 (= htslib version)
 - picard MarkDuplicatesWithMateCigar --version: 3.4.0


## Usage
To run the pipeline (after followig the installation instructions), navigate into the repo:

`cd tso500offtarget_ichorcna`

and then run the entrypoint script `drv_TSO500_offtarget_ichorCNA_parallel.sh` as follows:

`bash drv_TSO500_offtarget_ichorCNA_parallel.sh --indir <dir_path_with_indexed+aligned_TSO500ctDNA_BAMs> --ichorpath <path_to_your_ichorCNA_installation>`


## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
