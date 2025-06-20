docker run -it --rm \
	-v /mnt/NovaseqXplus:/mnt/NovaseqXplus \
	-v /mnt/Novaseq:/mnt/Novaseq \
	-v /staging:/staging \
	-v /var/log/dragen:/var/log/dragen \
	-v /var/lib/edico:/var/lib/edico \
	-v /opt/illumina/resource:/opt/illumina/resource \
	-v /var/run:/var/run \
	-v /var/lib/edico:/var/lib/edico \
	-v /var/log/dragen:/var/log/dragen \
	-v /var/run/dragen:/var/run/dragen \
	-v /dev/log:/dev/log \
	-v /dev/hugepages:/dev/hugepages \
	-v /dev/shm:/dev/shm \
	-v /usr/bin:/usr/bin \
	-v /usr/local:/usr/local \
	-v /usr/libexec:/usr/libexec \
	-v /opt:/opt \
	-v /root:/root \
	tso500_dragen_pipeline \
	/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh --runFolder /mnt/Novaseq/07_Oncoservice/Runs/250508_TSO500_Onco/250508_A01664_0504_AH32GTDMX2