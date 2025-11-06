# Add this to your ~/.bashrc or ~/.zshrc
alias go_to_testing_dir='export PATH="$(get_repo_root):$PATH"'

get_repo_root() {
    git rev-parse --show-toplevel 2>/dev/null
}
