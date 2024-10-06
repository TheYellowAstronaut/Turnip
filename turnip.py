from github import Github
import os, requests, zipfile, io, shutil, json
from github.GithubException import UnknownObjectException
from colorama import init, Fore, Back, Style

with open(rf'C:\turnip\config\cred.json', 'r') as file:
    input_dict = json.load(file)
for key, value in input_dict.items():
    globals()[key] = eval(value)
    
# GitHub setup
g = Github(GITHUB_TOKEN)

REPO_NAME = input(Fore.LIGHTMAGENTA_EX + f"\nGithub Repo: " + Fore.LIGHTBLACK_EX + f"{USERNAME}/" + Style.RESET_ALL)
REPO_ADD = f"{USERNAME}/{REPO_NAME}"
repo = g.get_repo(REPO_ADD)

DOWNLOAD_FOLDER = r"C:\turnip\sync"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Download and extract the repository
zip_url = f"https://github.com/{USERNAME}/{REPO_NAME}/archive/refs/heads/main.zip"
response = requests.get(zip_url)

if response.status_code == 200:
    shutil.rmtree(DOWNLOAD_FOLDER, ignore_errors=True)
    os.makedirs(DOWNLOAD_FOLDER)

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(DOWNLOAD_FOLDER)

    print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" Repository '{REPO_ADD}' downloaded and extracted to {DOWNLOAD_FOLDER}." + Style.RESET_ALL)
    folder = os.path.join(DOWNLOAD_FOLDER + f"\\{REPO_NAME}-main")
    os.rename(folder, folder[:-5])
else:
    print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" Failed to download repository. Status code: {response.status_code}" + Style.RESET_ALL)

print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" Session started on repository: '{REPO_ADD}'\n" + Style.RESET_ALL)

def delete_github_folder(repo, path):
    """Delete a folder and its contents on GitHub."""
    contents = repo.get_contents(path)
    for content in contents:
        if content.type == "dir":
            delete_github_folder(repo, content.path)
        else:
            try:
                repo.delete_file(content.path, f"Delete {content.path}", content.sha)
                print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" Deleted file '{content.path}' from GitHub." + Style.RESET_ALL)
            except Exception as e:
                print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" Error deleting file '{content.path}': {e}" + Style.RESET_ALL)

    try:
        repo.delete_file(path, f"Delete folder {path}", contents[0].sha)
        print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" Deleted folder '{path}' from GitHub." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" Error deleting folder '{path}': {e}" + Style.RESET_ALL)

def upload_files_to_github(local_folder, repo):
    """Upload or update files to GitHub."""
    local_files = set()

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, local_folder)
            github_path = relative_path.replace("\\", "/")
            local_files.add(github_path)

            try:
                with open(file_path, 'rb') as file_content:
                    try:
                        contents = repo.get_contents(github_path)
                        repo.update_file(contents.path, f"Update {github_path}", file_content.read(), contents.sha)
                    except UnknownObjectException:
                        try:
                            repo.create_file(github_path, f"Create {github_path}", file_content.read())
                        except UnknownObjectException:
                            pass
                    except Exception as e:
                        print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" Error with '{github_path}': {e}" + Style.RESET_ALL)
            except FileNotFoundError:
                print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" File not found: {file_path}" + Style.RESET_ALL)

    remote_files = repo.get_contents("")
    for content in remote_files:
        if content.path not in local_files:
            if content.type == "dir":
                delete_github_folder(repo, content.path)
            else:
                try:
                    repo.delete_file(content.path, f"Delete {content.path}", content.sha)
                    print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" Deleted '{content.path}' from GitHub as it no longer exists locally.")
                except Exception as e:
                    print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + f" Error deleting '{content.path}': {e}")

    print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + " Synced to Repo\n" + Style.RESET_ALL)


while True:
    cmd = input(Fore.LIGHTBLACK_EX + f"{REPO_ADD}"+ Style.RESET_ALL + Fore.LIGHTMAGENTA_EX + " | Turnip> " + Style.RESET_ALL)
    
    if cmd == "close":
        upload_folder = DOWNLOAD_FOLDER + f"\\{REPO_NAME}"
        upload_files_to_github(upload_folder, repo)
        shutil.rmtree(upload_folder, ignore_errors=True)
        print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + " Session closed\n" + Style.RESET_ALL)
        break
    elif cmd == "sync":
        upload_files_to_github(DOWNLOAD_FOLDER + f"\\{REPO_NAME}", repo)
    elif cmd == "close -dontsync":
        upload_folder = DOWNLOAD_FOLDER + f"\\{REPO_NAME}"
        shutil.rmtree(upload_folder, ignore_errors=True)
        print(Fore.LIGHTMAGENTA_EX + f"\nTurnip:~" + Fore.LIGHTBLACK_EX + " Session closed without syncing to repo\n" + Style.RESET_ALL)
        break
    elif cmd.startswith("$"):
        os.system(f"cd {DOWNLOAD_FOLDER + f"\\{REPO_NAME}"} && {cmd[1:]}")