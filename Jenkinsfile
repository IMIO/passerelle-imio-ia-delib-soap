@Library('eo-jenkins-lib@master') import eo.Utils

pipeline {
    agent any
    stages {
        stage('Packaging') {
            steps {
                script {
                    if (env.JOB_NAME == 'passerelle-imio-ia-delib' && env.GIT_BRANCH == 'origin/master') {
                        sh 'sudo -H -u eobuilder /usr/local/bin/eobuilder passerelle-imio-ia-delib'
                    } else if (env.GIT_BRANCH.startsWith('hotfix/')) {
                        sh "sudo -H -u eobuilder /usr/local/bin/eobuilder --branch ${env.GIT_BRANCH} --hotfix passerelle-imio-ia-delib"
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                utils = new Utils()
                utils.mail_notify(currentBuild, env, 'admin+jenkins-passerelle-imio-ia-delib@entrouvert.com')
            }
        }
        success {
            cleanWs()
        }
    }
}
