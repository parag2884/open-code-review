from app.security import validate_git_url


def test_rejects_non_https():
    try:
        validate_git_url("http://github.com/org/repo", {"github.com"})
        assert False, "expected failure"
    except ValueError:
        pass


def test_rejects_credentials():
    try:
        validate_git_url("https://user:pass@github.com/org/repo", {"github.com"})
        assert False, "expected failure"
    except ValueError:
        pass


def test_rejects_unknown_host():
    try:
        validate_git_url("https://evil.example/org/repo", {"github.com"})
        assert False, "expected failure"
    except ValueError:
        pass


def test_accepts_github_https():
    url = validate_git_url("https://github.com/org/repo.git", {"github.com"})
    assert url == "https://github.com/org/repo.git"


if __name__ == "__main__":
    test_rejects_non_https()
    test_rejects_credentials()
    test_rejects_unknown_host()
    test_accepts_github_https()
    print("security tests passed")
