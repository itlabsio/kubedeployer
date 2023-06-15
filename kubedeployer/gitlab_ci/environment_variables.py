import os

from kubedeployer.gitlab_ci import specification
from kubedeployer.gitlab_ci.variable_reader import AbstractVariableReader, EnvironmentVariableReader
from kubedeployer.gitlab_ci.variable_types import StrVariable, BoolVariable, \
    IntVariable


class Settings:
    def __init__(self):
        self._variable_reader = EnvironmentVariableReader()

    def _set_variable_reader(self, reader: AbstractVariableReader):
        """
        Set other variable reader (used for tests).
        """
        self._variable_reader = reader

    @property
    def environment(self) -> StrVariable:
        """
        Deployment environment.
        """
        return self._variable_reader.read_str(specification.ENVIRONMENT_ENV_VAR)

    @property
    def show_manifests(self) -> BoolVariable:
        """
        Show applying manifests in log.
        """
        return self._variable_reader.read_bool(specification.SHOW_MANIFESTS_ENV_VAR, default_value=False)

    @property
    def ci_registry(self) -> StrVariable:
        """
        The address of the project’s Container Registry.
        """
        return self._variable_reader.read_str(specification.CI_REGISTRY_ENV_VAR)

    @property
    def ci_project_id(self) -> StrVariable:
        """
        The ID of the current project. This ID is unique across all projects on
        the GitLab instance.
        """
        return self._variable_reader.read_str(specification.CI_PROJECT_ID_ENV_VAR, is_required=True)

    @property
    def ci_project_dir(self) -> StrVariable:
        """
        The full path the repository is cloned to, and where the job runs from.
        If the GitLab Runner builds_dir parameter is set, this variable is set
        relative to the value of builds_dir.
        """
        default_value = os.getcwd()
        return self._variable_reader.read_str(specification.CI_PROJECT_DIR_ENV_VAR, default_value=default_value)

    @property
    def ci_commit_sha(self) -> StrVariable:
        """
        The commit revision the project is built for.
        """
        return self._variable_reader.read_str(specification.CI_COMMIT_SHA_ENV_VAR, is_required=True)

    @property
    def ci_commit_ref_name(self) -> StrVariable:
        """
        The branch or tag name for which project is built.
        """
        return self._variable_reader.read_str(specification.CI_COMMIT_REF_NAME_ENV_VAR, is_required=False)

    @property
    def ci_commit_branch(self) -> StrVariable:
        """
        The commit branch name. Available in branch pipelines, including
        pipelines for the default branch.
        """
        return self._variable_reader.read_str(specification.CI_COMMIT_BRANCH_ENV_VAR)

    @property
    def ci_commit_tag(self) -> StrVariable:
        """
        The commit tag name. Available only in pipelines for tags.
        """
        return self._variable_reader.read_str(specification.CI_COMMIT_TAG_ENV_VAR)

    @property
    def gitlab_user_id(self) -> StrVariable:
        """
        The ID of the user who started the job.
        """
        return self._variable_reader.read_str(specification.GITLAB_USER_ID_ENV_VAR, is_required=True)

    @property
    def kube_url(self) -> StrVariable:
        """
        Kubernetes url where need to deploy application.
        """
        return self._variable_reader.read_str(specification.KUBE_URL_ENV_VAR, is_required=True)

    @property
    def kube_token(self) -> StrVariable:
        """
        Kubernetes access token.
        """
        return self._variable_reader.read_str(specification.KUBE_TOKEN_ENV_VAR, default_value='')

    @property
    def kube_namespace(self) -> StrVariable:
        """
        Kubernetes namespace where application will be deployed by default if
        namespace not set in manifests.
        """
        return self._variable_reader.read_str(specification.KUBE_NAMESPACE_ENV_VAR, default_value='default')

    @property
    def kube_verbosity(self) -> IntVariable:
        """
        Kubectl log level from 0 to 9
        (https://kubernetes.io/docs/reference/kubectl/cheatsheet/#kubectl-output-verbosity-and-debugging).
        """
        verbosity = self._variable_reader.read_int(specification.KUBE_VERBOSITY_ENV_VAR, default_value=2)
        verbosity.value %= specification.KUBE_VERBOSITY_BASE
        return verbosity

    @property
    def manifest_folder(self) -> StrVariable:
        """
        Directory inside project where manifests are located.
        """
        return self._variable_reader.read_str(specification.MANIFEST_FOLDER_ENV_VAR, is_required=True)

    @property
    def deploy_wait_timeout(self):
        """
        Kubectl rollout timeout.
        """
        return self._variable_reader.read_str(specification.DEPLOY_WAIT_TIMEOUT_ENV_VAR, default_value='10m')

    @property
    def ci_runner_tags(self) -> StrVariable:
        """
        A comma-separated list of the runner tags.
        """
        return self._variable_reader.read_str(specification.CI_RUNNER_TAGS_ENV_VAR)

    @property
    def ci_job_id(self) -> StrVariable:
        """
        The internal ID of the job, unique across all jobs in the GitLab instance.
        """
        return self._variable_reader.read_str(specification.CI_JOB_ID_ENV_VAR, is_required=True)

    @property
    def ci_pipeline_id(self) -> StrVariable:
        """
        The instance-level ID of the current pipeline. This ID is unique across
        all projects on the GitLab instance.
        """
        return self._variable_reader.read_str(specification.CI_PIPELINE_ID_ENV_VAR, is_required=True)

    @property
    def ci_job_author(self) -> StrVariable:
        """
        The email of the user who started the job.
        """
        return self._variable_reader.read_str(specification.GITLAB_USER_EMAIL_ENV_VAR)

    @property
    def ci_job_url(self) -> StrVariable:
        """
        The job details URL.
        """
        return self._variable_reader.read_str(specification.CI_JOB_URL_ENV_VAR)

    @property
    def project_url(self) -> StrVariable:
        """
        The HTTP(S) address of the project.
        """
        return self._variable_reader.read_str(specification.CI_PROJECT_URL_ENV_VAR)

    @property
    def vault_url(self) -> StrVariable:
        """
        The HTTPS address of the Vault.
        """
        return self._variable_reader.read_str(specification.VAULT_URL_ENV_VAR)

    @property
    def vault_approle_id(self) -> StrVariable:
        """
        The approle auth method allows machines or apps to authenticate with
        Vault-defined roles.
        """
        return self._variable_reader.read_str(specification.VAULT_APPROLE_ID_ENV_VAR)

    @property
    def vault_approle_secret_id(self) -> StrVariable:
        """
        App_role secret id для подключения к vault
        """
        return self._variable_reader.read_str(specification.VAULT_APPROLE_SECRET_ENV_VAR)

    @property
    def vault_secret_prefix(self) -> StrVariable:
        """
        Vault Approle secret id.
        """
        return self._variable_reader.read_str(specification.VAULT_SECRETS_PREFIX_ENV_VAR)

    @property
    def trivy_image_template(self) -> StrVariable:
        """
        Template that allows filtering docker image names for Trivy.
        """
        return self._variable_reader.read_str(specification.TRIVY_IMAGE_TEMPLATE_ENV_VAR)


settings = Settings()
