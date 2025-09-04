docker build ichorCNA /home/matvii/PycharmProjects/TSO_500_DRAGEN_pipeline/sandbox/ichorCNA_docker

docker run -it \
  -v /home/matvii/PycharmProjects/TSO_500_DRAGEN_pipeline/sandbox/ichorCNA_docker:/tmp \
  -v /media/matvii/30c92328-1f20-448d-a014-902558a05393/data:/tmp/test \
  ichorCNA

