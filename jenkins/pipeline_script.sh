pipeline {
  agent {node {label 'master'}}

  environment {
    PATH="/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin"
  }

  parameters {
    choice(
      choices: 'dev\nprod',
      description: 'Choose deploy environment',
      name: 'deploy_env'
    )
    choice(
      choices: 'yes\nno',
      description: 'Do you want to override the installation?',
      name: 'cover_install'
    )
    choice(
      choices: ['docker', 'EasyDarwin', 'frp', 'hk_camera', 'mysqlData', 'nginx', 'php_conf', 'rath', 'script', 'socket_server', 'camera_admin', 'model_update'],
      description: 'Select the app to deploy',
      name: 'task_category'
    )
	}

  stages{
    stage("Folder check") {
      steps{
        echo "[INFO] Folder check start."
        // docker,EasyDarwin,frp,hk_camera,mysqlData,nginx,php_conf,rath,script,socket_server
        script {
          switch (task_category) {
            case 'docker':
              env.project_name = 'ring_docker_config'
              env.folder_name = 'docker'
              break
            case 'EasyDarwin':
              env.project_name = 'ring_easydarwin'
              env.folder_name = 'EasyDarwin'
              break
            case 'frp':
              env.project_name = 'ring_frp'
              env.folder_name = 'frp'
              break
            case 'hk_camera':
              env.project_name = 'ring_hk_camera'
              env.folder_name = 'hk_camera'
              break
            case 'mysqlData':
              env.project_name = 'ring_mysqldata'
              env.folder_name = 'mysqlData'
              break
            case 'nginx':
              env.project_name = 'ring_nginx'
              env.folder_name = 'nginx'
              break
            case 'php_conf':
              env.project_name = 'ring_php_conf'
              env.folder_name = 'php_conf'
              break
            case 'rath':
              env.project_name = 'ring_rath'
              env.folder_name = 'rath'
              break
            case 'script':
              env.project_name = 'ring_script'
              env.folder_name = 'script'
              break
            case 'socket_server':
              env.project_name = 'ring_socket_server'
              env.folder_name = 'socket_server'
              break
            case 'camera_admin':
              env.project_name = 'ring_camera_admin'
              env.folder_name = 'nginx'
              break
            case 'model_update':
              env.project_name = 'ring_model_update'
              env.folder_name = 'model_update'
          }
        }
        dir ("${env.WORKSPACE}/ring_ansible_deploy"){
          sh """
            if [ ! -d "ring_ansible_deploy" ]; then
              mkdir ring_ansible_deploy
            fi
          """
        }
        echo "[INFO] Folder check end."
      }
    }

    stage("Pull Ansible deploy script") {
      steps {
        echo "[INFO] Pull Ansible deploy script start ... "
        dir ("${env.WORKSPACE}/ring_ansible_deploy"){
          git credentialsId: 'edc589de-1a46-46ac-a53c-a4775ee2409c', url: 'http://192.168.10.5:9980/fuxi/ring_ansible_deploy.git'
        }
        echo "[INFO] Pull Ansible deploy script finished ... "
      }
    }

    stage("Ansible deploy") {
      steps {
        echo "[INFO] Ansible deploy start."
        dir("${env.WORKSPACE}/ring_ansible_deploy") {
          sh """
          ansible-playbook -i inventory/$deploy_env ./deploy.yml \
            --extra-vars "ansible_become_pass=fuxig2604" \
            -e env=$deploy_env \
            -e deploy_folder=${env.folder_name} \
            -e task_type=${env.project_name} \
            -e cover_install=$cover_install
          """
        }
        echo "[INFO] Ansible deploy end."
      }
    }
  }
}
