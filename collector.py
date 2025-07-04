import os
import requests
import random
import base64

PROTOCOLS = {
    'vmess': 'vmess://',
    'vless': 'vless://',
    'trojan': 'trojan://',
    'shadowsocks': 'ss://',
    'hysteria': 'hysteria://',
    'hysteria2': 'hysteria2://',
    'reality': 'reality://',
    'tuic': 'tuic://',
    'ssh': 'ssh://'
}

def get_repo_tree(owner, repo, branch="main"):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json().get('tree', [])
    except Exception as e:
        print(f"[ERROR] Cannot get repo tree for {owner}/{repo}: {e}")
        return []

def filter_relevant_files(tree):
    allowed_ext = ['.txt', '.list', '.conf', '.json', '.log']
    return [item['path'] for item in tree if item['type'] == 'blob' and any(item['path'].lower().endswith(ext) for ext in allowed_ext)]

def fetch_raw_file(owner, repo, filepath, branch="main"):
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filepath}"
    try:
        r = requests.get(raw_url, timeout=15)
        r.raise_for_status()
        return r.text.splitlines()
    except Exception as e:
        print(f"[ERROR] Cannot fetch raw file {filepath} from {owner}/{repo}: {e}")
        return []

def clean_link(link: str) -> str | None:
    # حذف بخش توضیحی بعد از #
    link = link.split('#')[0].strip()

    if link.startswith("ss://"):
        encoded = link[5:]
        try:
            base64.b64decode(encoded + '=' * (-len(encoded) % 4))
            return link + '#@F0rc3Run'
        except Exception:
            return None  # اگر خراب بود حذف شود
    else:
        return link + '#@F0rc3Run'

def main():
    configs = {p: [] for p in PROTOCOLS}
    repos = os.getenv("VPN_REPOS", "").splitlines()
    print("[DEBUG] VPN_REPOS:", repos)

    if not repos:
        print("[ERROR] VPN_REPOS environment variable is empty!")
        return

    for repo_line in repos:
        repo_line = repo_line.strip()
        if not repo_line or '/' not in repo_line:
            continue
        owner, repo = repo_line.split('/', 1)
        print(f"[INFO] Processing repo: {owner}/{repo}")
        tree = get_repo_tree(owner, repo)
        if not tree:
            continue
        files = filter_relevant_files(tree)
        for file_path in files:
            lines = fetch_raw_file(owner, repo, file_path)
            for line in lines:
                line = line.strip()
                for proto, prefix in PROTOCOLS.items():
                    if line.startswith(prefix):
                        cleaned = clean_link(line)
                        if cleaned:
                            configs[proto].append(cleaned)
                        break

    MIN_SERVERS = 1
    MAX_SERVERS = 1000
    os.makedirs("configs", exist_ok=True)

    for proto, lines in configs.items():
        unique_lines = list(set(lines))
        count = len(unique_lines)
        if count == 0:
            print(f"[WARN] پروتکل {proto} سروری ندارد.")
            continue
        selected_count = max(MIN_SERVERS, min(count, MAX_SERVERS))
        if count >= selected_count:
            selected = random.sample(unique_lines, selected_count)
        else:
            selected = unique_lines
        file_path = f"configs/{proto}.txt"
        with open(file_path, "w") as f:
            f.write("\n".join(selected))
        print(f"[INFO] فایل {file_path} با {len(selected)} سرور ذخیره شد.")

if __name__ == "__main__":
    main()
