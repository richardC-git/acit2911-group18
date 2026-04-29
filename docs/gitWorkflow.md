## GitHub Workflow

### 1. Branching

- `main` = stable project branch
- Each member creates their own feature branch for **every** new feature addition

Branch name format:

```bash
feature/short-description
```

Example:

```bash
feature/readme-update
```

### 2. Making Changes

Before starting work:

```bash
git pull origin main
git checkout -b feature/your-change
```

After making changes:

```bash
git add .
git commit -m "Describe your change"
git push origin feature/your-change
```

### 3. Pull Requests

Open a Pull Request into main
Add a short description of what changed
At least one team member should review before merging

### 4. Commit Style

Use simple, clear commit messages:

```bash
Add README project structure
Update documentation
Fix folder naming
```

### 5. Basic Rules

- Do not commit directly to main
- Pull from main before starting new work
- Keep commits small and focused
- Communicate before editing the same files
