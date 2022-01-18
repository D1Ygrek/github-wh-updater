def check_commit(commit_text):
    if commit_text.find('deploy--version') != -1:
        commit_text = commit_text.replace('deploy--version','')
        return True, commit_text.replace(' ', '')
    else:
        return False, None