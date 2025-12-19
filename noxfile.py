import nox
from nox import Session

# Define Python versions you want to test
PYTHON_VERSIONS: list[str] = ["3.10", "3.11"]

# Define Django versions you want to test
DJANGO_VERSIONS: list[str] = ["4.0.10", "4.2.27"]


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("django", DJANGO_VERSIONS)
def tests(session: Session, django: str) -> None:
    """Run tests with different Python and Django versions."""
    # Skip incompatible combinations if you add Django 5.0+
    # if session.python == "3.9" and django in ["5.0", "5.1"]:
    #     session.skip("Django 5.0+ requires Python 3.10+")

    session.install(f"django=={django}")
    session.install("pytest", "pytest-django")
    session.install(".")  # Install your package
    session.run("pytest", "-v", env={"DJANGO_SETTINGS_MODULE": "money.tests.settings"})
