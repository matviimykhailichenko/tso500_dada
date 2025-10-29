
# I set down this out of R
  git config --global user.email "r8a8m8p8@gmail.com"
  git config --global user.name "raulmejia"

library("usethis")
usethis::create_github_token()
### It will redirect you to  'https://github.com/settings/tokens/new?scopes=repo,user,gist,workflow&description=DESCRIBE THE TOKEN\'S USE CASE'  There you can finisth the formular to create your token

# copy and paste your token on this command
gitcreds::gitcreds_set()  # Paste your credential there
git_vaccinate() # some optional recomended command

usethis::git_sitrep() #  For checking

# If you are here for installing ichorCNA, now you can do
# lliibrary("devtools")
# install_github("broadinstitute/ichorCNA")

###############
# References: 
#################
# https://bookdown.org/amy_yarnell/T32-book/get-a-personal-access-token-pat.html
# https://usethis.r-lib.org/articles/git-credentials.html
