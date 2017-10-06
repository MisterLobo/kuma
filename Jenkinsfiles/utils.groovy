/*
 * Define utility functions.
 */

def checkout_github(repo, branch, relative_target_dir) {
    checkout(
        [$class: 'GitSCM',
         userRemoteConfigs: [[url: "https://github.com/${repo}"]],
         branches: [[name: "refs/heads/${branch}"]],
         extensions: [[$class: 'RelativeTargetDirectory',
                       relativeTargetDir: relative_target_dir]],
         doGenerateSubmoduleConfigurations: false,
         submoduleCfg: []]
    )
}

def make(setup, cmd) {
    sh """
        . ${setup}
        ls -la ~/.kube
        make ${cmd} KUMA_IMAGE_TAG=${env.GIT_COMMIT_SHORT}
    """
}

def make_stage(cmd) {
    make('regions/portland/stage.sh', cmd)
}

def migrate_stage_db() {
    make_stage('k8s-db-migration-job')
}

def deploy_kuma_to_stage() {
    make_stage('k8s-kuma-deployments')
}

def monitor_deploy_kuma_to_stage() {
    make_stage('k8s-kuma-rollout-status')
}

return this;
