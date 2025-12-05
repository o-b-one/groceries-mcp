# Git Commit Workflow with Semantic Commit Guidelines

This workflow making commits in this project, ensuring adherence to Conventional Commits for a clean and automated commit history.

## Workflow Steps:

**1: Review Git Changes**

Before committing, always review the changes you've made to ensure they are intended and complete.

```bash
git status
```
This command shows which files have been modified, added, or deleted.


```bash
git diff
```
This command displays the line-by-line changes in your modified files.

**2: Stage Your Changes**

Selectively add the files you want to include in your commit to the staging area.

    ```bash
    git add <file_path>
    ```
    Replace `<file_path>` with the path to the file you want to stage.

Alternative
```bash
git add .
```
Use this with caution, ensuring you've reviewed all changes first.

**3: Generate Commit Message (Semantic Commit)**

Craft your commit message following the Conventional Commits specification. Each commit message consists of a **header**, an optional **body**, and an optional **footer**.

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

#### Commit Message Elements:

1.  **type**: (required)
    *   `feat`: A new feature
    *   `fix`: A bug fix
    *   `docs`: Documentation only changes
    *   `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.)
    *   `refactor`: A code change that neither fixes a bug nor adds a feature
    *   `perf`: A code change that improves performance
    *   `test`: Adding missing tests or correcting existing tests
    *   `build`: Changes that affect the build system or external dependencies
    *   `ci`: Changes to our CI configuration files and scripts
    *   `chore`: Other changes that don't modify src or test files
    *   `revert`: Reverts a previous commit

2.  **scope**: (optional) Describes the area of the codebase affected (e.g., `retail_agent`, `shufersal-mcp`, `docs`, `server`).

3.  **subject**: (required) A very short, succinct description of the change.
    *   Use the imperative, present tense: "change" not "changed" nor "changes"
    *   Don't capitalize the first letter
    *   No period (.) at the end

4.  **body**: (optional) A longer description providing additional context.
    *   Use the imperative, present tense.
    *   Explain the "what" and "why" of the change, not the "how".

5.  **footer**: (optional) For breaking changes and issue references.
    *   **Breaking Changes**: Start with `BREAKING CHANGE:`
    *   **References**: Reference issues by their full URL, e.g., `Closes #123` or `Fixes https://github.com/owner/repo/issues/123`

#### Example Commit Messages:

```
feat(retail_agent): add new product search functionality

This commit introduces a new product search feature in the retail agent.
Users can now search for products using keywords, and the agent will
return relevant results from the integrated grocery providers.

BREAKING CHANGE: The old 'search_by_id' endpoint has been deprecated.
Please use the new 'search_products' endpoint with keyword parameters.
Refs #456
```

```
fix(shufersal-mcp): correct cart item quantity update

Fixes an issue where updating the quantity of items in the Shufersal
cart would sometimes result in incorrect totals due to a race condition.
Implemented a transactional update to ensure data consistency.
```

**4: Perform Git Commit**

Once your changes are staged and your commit message is ready, perform the commit.

```bash
git commit -m "<type>(<scope>): <subject>" -m "<body>" -m "<footer>"
```
For simpler commits, you can use `git commit -m "<type>(<scope>): <subject>"`. For more complex messages, use a text editor by running `git commit` without the `-m` flag.

