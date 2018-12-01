
# coding: utf-8

# In[15]:


import os
import numpy as np
import csv


# In[16]:


nti_type = 'linear'
nti_dim_x = '17'
nti_dim_y = '17'
#Src
capture_src = os.getcwd()
#Train
csv_output_train_data = 'ntis_%s_%sx%s_train_data.csv' % (nti_type,nti_dim_x,nti_dim_y)
csv_output_train_target_bulk_vs_all = 'ntis_%s_%sx%s_train_target_bulk_vs_all.csv' % (nti_type,nti_dim_x,nti_dim_y)
csv_output_train_target_qos = 'ntis_%s_%sx%s_train_target_qos.csv' % (nti_type,nti_dim_x,nti_dim_y)
csv_output_train_target_classes = 'ntis_%s_%sx%s_train_target_classes.csv' % (nti_type,nti_dim_x,nti_dim_y)
#Test
csv_output_test_data = 'ntis_%s_%sx%s_test_data.csv' % (nti_type,nti_dim_x,nti_dim_y)
csv_output_test_target_bulk_vs_all = 'ntis_%s_%sx%s_test_target_bulk_vs_all.csv' % (nti_type,nti_dim_x,nti_dim_y)
csv_output_test_target_qos = 'ntis_%s_%sx%s_test_target_qos.csv' % (nti_type,nti_dim_x,nti_dim_y)
csv_output_test_target_classes = 'ntis_%s_%sx%s_test_target_classes.csv' % (nti_type,nti_dim_x,nti_dim_y)

#0day-Test
csv_output_test_0day_data = 'ntis_%s_%sx%s_test_0day_data.csv' % (nti_type,nti_dim_x,nti_dim_y)
csv_output_test_target_0day_bulk_vs_all = 'ntis_%s_%sx%s_test_0day_target_bulk_vs_all.csv' % (nti_type,nti_dim_x,nti_dim_y)
csv_output_test_target_0day_qos = 'ntis_%s_%sx%s_test_0day_target_qos.csv' % (nti_type,nti_dim_x,nti_dim_y)
csv_output_test_target_0day_classes = 'ntis_%s_%sx%s_test_0day_target_classes.csv' % (nti_type,nti_dim_x,nti_dim_y)


# In[17]:


#Open all Relevant File Handles
csv_output_train_data_file = open(csv_output_train_data,'w')
csv_output_train_target_bulk_vs_all_file = open(csv_output_train_target_bulk_vs_all,'w')
csv_output_train_target_qos_file = open(csv_output_train_target_qos,'w')
csv_output_train_target_classes_file = open(csv_output_train_target_classes,'w')

csv_output_test_data_file = open(csv_output_test_data,'w')
csv_output_test_target_bulk_vs_all_file = open(csv_output_test_target_bulk_vs_all,'w')
csv_output_test_target_qos_file = open(csv_output_test_target_qos,'w')
csv_output_test_target_classes_file = open(csv_output_test_target_classes,'w')

csv_output_test_0day_data_file = open(csv_output_test_0day_data,'w')
csv_output_test_target_0day_bulk_vs_all_file = open(csv_output_test_target_0day_bulk_vs_all,'w')
csv_output_test_target_0day_qos_file = open(csv_output_test_target_0day_qos,'w')
csv_output_test_target_0day_classes_file = open(csv_output_test_target_0day_classes,'w')

#CLASS_TARGETS: 0=game,1=video_conferencing,2=streams,3=bulk_download,4=torrents
#QOS_TARGETS: 0=game,video_conferencing,1=streams,2=bulk_download,torrents
#BULK_TARGETS: 0=game,video_conferencing,streams, 1=bulk_download,torrents

try:
	#TODO: Open csv_output_train and csv_output_target file handles.
	for x in os.walk(capture_src): #each os.walk element is: dirpath, subdir-names, dir-filenames
		for file in x[2]:
			if file.endswith(".nti"):
				packet_lengths = list()
				with open(x[0]+ os.sep + file,'r') as nti:
					for line in nti:
						packet_lengths += line.rstrip().split(" ")
				nti_csv = ",".join(packet_lengths) + "\n"
			
				if("train" in x[0]):
					csv_output_train_data_file.write(nti_csv)
					if("game" in x[0]):
						csv_output_train_target_bulk_vs_all_file.write("0\n")
						csv_output_train_target_qos_file.write("0\n")
						csv_output_train_target_classes_file.write("0\n")
					elif("video_conferencing" in x[0]):
						csv_output_train_target_bulk_vs_all_file.write("0\n")
						csv_output_train_target_qos_file.write("0\n")
						csv_output_train_target_classes_file.write("1\n")
					elif("stream" in x[0]):
						csv_output_train_target_bulk_vs_all_file.write("0\n")
						csv_output_train_target_qos_file.write("1\n")
						csv_output_train_target_classes_file.write("2\n")
					elif("bulk_download" in x[0]):
						csv_output_train_target_bulk_vs_all_file.write("1\n")
						csv_output_train_target_qos_file.write("2\n")
						csv_output_train_target_classes_file.write("3\n")
					elif("torrent" in x[0]):
						csv_output_train_target_bulk_vs_all_file.write("1\n")
						csv_output_train_target_qos_file.write("2\n")
						csv_output_train_target_classes_file.write("4\n")
				elif("0day" in x[0]):
					csv_output_test_0day_data_file.write(nti_csv)
					if("game" in x[0]):
						csv_output_test_target_0day_bulk_vs_all_file.write("0\n")
						csv_output_test_target_0day_qos_file.write("0\n")
						csv_output_test_target_0day_classes_file.write("0\n")
					elif("video_conferencing" in x[0]):
						csv_output_test_target_0day_bulk_vs_all_file.write("0\n")
						csv_output_test_target_0day_qos_file.write("0\n")
						csv_output_test_target_0day_classes_file.write("1\n")
					elif("stream" in x[0]):
						csv_output_test_target_0day_bulk_vs_all_file.write("0\n")
						csv_output_test_target_0day_qos_file.write("1\n")
						csv_output_test_target_0day_classes_file.write("2\n")
					elif("bulk_download" in x[0]):
						csv_output_test_target_0day_bulk_vs_all_file.write("1\n")
						csv_output_test_target_0day_qos_file.write("2\n")
						csv_output_test_target_0day_classes_file.write("3\n")
					elif("torrent" in x[0]):
						csv_output_test_target_0day_bulk_vs_all_file.write("1\n")
						csv_output_test_target_0day_qos_file.write("2\n")
						csv_output_test_target_0day_classes_file.write("4\n")
				else: #test
					csv_output_test_data_file.write(nti_csv)
					if("game" in x[0]):
						csv_output_test_target_bulk_vs_all_file.write("0\n")
						csv_output_test_target_qos_file.write("0\n")
						csv_output_test_target_classes_file.write("0\n")
					elif("video_conferencing" in x[0]):
						csv_output_test_target_bulk_vs_all_file.write("0\n")
						csv_output_test_target_qos_file.write("0\n")
						csv_output_test_target_classes_file.write("1\n")
					elif("stream" in x[0]):
						csv_output_test_target_bulk_vs_all_file.write("0\n")
						csv_output_test_target_qos_file.write("1\n")
						csv_output_test_target_classes_file.write("2\n")
					elif("bulk_download" in x[0]):
						csv_output_test_target_bulk_vs_all_file.write("1\n")
						csv_output_test_target_qos_file.write("2\n")
						csv_output_test_target_classes_file.write("3\n")
					elif("torrent" in x[0]):
						csv_output_test_target_bulk_vs_all_file.write("1\n")
						csv_output_test_target_qos_file.write("2\n")
						csv_output_test_target_classes_file.write("4\n")
except KeyboardInterrupt:
	pass

#Close all relevant file handles
csv_output_train_data_file.close()
csv_output_train_target_bulk_vs_all_file.close()
csv_output_train_target_qos_file.close()
csv_output_train_target_classes_file.close()

csv_output_test_data_file.close()
csv_output_test_target_bulk_vs_all_file.close()
csv_output_test_target_qos_file.close()
csv_output_test_target_classes_file.close()

csv_output_test_0day_data_file.close()
csv_output_test_target_0day_bulk_vs_all_file.close()
csv_output_test_target_0day_qos_file.close()
csv_output_test_target_0day_classes_file.close()
print("Job Done!")

