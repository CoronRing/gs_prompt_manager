# Setting Up PyPI Publishing with GitHub Actions

This guide explains how to configure automatic publishing to PyPI using GitHub Actions for the `gs_prompt_manager` package.

## Overview

The repository includes two GitHub Actions workflows:
1. **tests.yml** - Runs tests on every push and pull request
2. **publish-to-pypi.yml** - Publishes to PyPI when a release is created

## Prerequisites

Before you can publish to PyPI, you need to:

1. Have a [PyPI account](https://pypi.org/account/register/)
2. Have a [TestPyPI account](https://test.pypi.org/account/register/) (for testing)
3. Have admin access to the GitHub repository

## Setup Methods

There are two ways to authenticate with PyPI:

### Method 1: Trusted Publishing (Recommended)

Trusted publishing uses OpenID Connect (OIDC) and doesn't require manually creating tokens.

#### Steps:

1. **Configure PyPI Trusted Publisher**
   - Go to https://pypi.org/manage/account/publishing/
   - Click "Add a new pending publisher"
   - Fill in:
     - **PyPI Project Name**: `gs_prompt_manager`
     - **Owner**: `CoronRing` (your GitHub username/org)
     - **Repository name**: `gs_prompt_manager`
     - **Workflow name**: `publish-to-pypi.yml`
     - **Environment name**: `pypi`

2. **Configure TestPyPI Trusted Publisher** (optional, for testing)
   - Go to https://test.pypi.org/manage/account/publishing/
   - Follow the same steps as above

3. **Create GitHub Environment**
   - Go to your GitHub repo → Settings → Environments
   - Create an environment named `pypi`
   - (Optional) Add protection rules like requiring reviewers

That's it! The workflow is already configured to use trusted publishing.

### Method 2: API Token (Alternative)

If you prefer using API tokens:

1. **Generate PyPI API Token**
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Name it (e.g., "GitHub Actions")
   - Scope: "Entire account" or specific project
   - Copy the token (starts with `pypi-`)

2. **Add Token to GitHub Secrets**
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Paste your PyPI token

3. **Update Workflow File**
   - Edit `.github/workflows/publish-to-pypi.yml`
   - In the `publish-to-pypi` job, uncomment the password line:
     ```yaml
     - name: Publish to PyPI
       uses: pypa/gh-action-pypi-publish@release/v1
       with:
         password: ${{ secrets.PYPI_API_TOKEN }}
     ```

4. **Repeat for TestPyPI** (optional)
   - Generate token at https://test.pypi.org/manage/account/token/
   - Add as `TEST_PYPI_API_TOKEN` secret

## Publishing a Release

### Automatic Publishing (on Release)

1. Go to your GitHub repo → Releases → Draft a new release
2. Create a new tag (e.g., `v0.0.5`)
3. Fill in release title and description
4. Click "Publish release"
5. GitHub Actions will automatically:
   - Run all tests
   - Build the package
   - Publish to PyPI

### Manual Publishing (workflow_dispatch)

For testing or manual releases:

1. Go to Actions → "Publish to PyPI"
2. Click "Run workflow"
3. Select the branch
4. Click "Run workflow"
5. This will publish to TestPyPI (not production PyPI)

## Version Management

Before creating a release, update the version number:

1. Edit `pyproject.toml`
2. Update the version field:
   ```toml
   version = "0.0.5"
   ```
3. Commit and push
4. Then create the release with matching tag

## Workflow Overview

### Tests Workflow
- **Trigger**: Every push and pull request to main/master/develop
- **Runs on**: Ubuntu, Windows, macOS
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Steps**:
  1. Checkout code
  2. Set up Python
  3. Install dependencies
  4. Run pytest with coverage
  5. Upload coverage to Codecov (optional)

### Publish Workflow
- **Trigger**: When a release is published or manual trigger
- **Steps**:
  1. **Test Job**: Runs full test suite on all Python versions
  2. **Build Job**: Builds source and wheel distributions
  3. **Publish Job**: Publishes to PyPI using trusted publishing

## Troubleshooting

### Tests Fail
- Check the Actions tab for detailed error logs
- Run tests locally: `pytest test/ -v`
- Ensure all dependencies are installed: `pip install -e .`

### Publishing Fails
- **"403 Forbidden"**: Check trusted publisher configuration
- **"Invalid credentials"**: Verify API token is correct
- **"Package already exists"**: Update version number in `pyproject.toml`
- **"Project name mismatch"**: Ensure package name matches PyPI project

### Coverage Upload Fails
- This is non-critical and won't fail the workflow
- Check Codecov integration is set up correctly

## Local Build and Test

Before publishing, test locally:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the distribution
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ gs_prompt_manager
```

## Security Best Practices

1. **Never commit tokens** to the repository
2. **Use trusted publishing** when possible (more secure)
3. **Enable branch protection** for main/master branch
4. **Require PR reviews** before merging
5. **Use GitHub Environments** with required reviewers for production

## Next Steps

After setup:
1. Push changes to main branch
2. Verify tests pass in GitHub Actions
3. Create a test release to verify publishing works
4. Monitor the first few releases to ensure everything works correctly

## Support

- [PyPI Help](https://pypi.org/help/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
