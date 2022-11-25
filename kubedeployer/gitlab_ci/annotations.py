from typing import Dict

from kubedeployer.gitlab_ci.environment_variables import settings
from kubedeployer.gitlab_ci import specification


def get_annotations() -> Dict[str, str]:
    return {
        specification.ANNOTATION_CI_COMMIT_REF: settings.ci_commit_ref_name.value,
        specification.ANNOTATION_CI_JOB_REF: settings.ci_job_url.value,
        specification.ANNOTATION_CI_JOB_AUTHOR: settings.ci_job_author.value,
        specification.ANNOTATION_CI_REPO_URL: settings.project_url.value,
        specification.ANNOTATION_CI_PROJECT_ID: settings.ci_project_id.value,
        specification.ANNOTATION_CI_COMMIT_BRANCH: settings.ci_commit_branch.value,
        specification.ANNOTATION_CI_COMMIT_TAG: settings.ci_commit_tag.value
    }
