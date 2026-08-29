# GitHub publication

```bash
git init -b main
git config user.name "YOUR NAME"
git config user.email "YOUR PUBLIC EMAIL"
git add .
git commit -m "Initial reproducibility release"
git remote add origin https://github.com/ACCOUNT/REPOSITORY.git
git push -u origin main
```

Run `bash tools/verify_release.sh --full` before each tagged release.

