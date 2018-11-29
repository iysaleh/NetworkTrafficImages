
# coding: utf-8

# In[1]:


import matplotlib
import re
import os
import sys
import time
from datetime import datetime, timedelta
import numpy as np

##CurrentStep: Prograam global time-based NTI logic -- Maybe maybe make packet iterator with time parameters.

#Just a note-- Consider heuristics to determine whether a time based NTI is valid --
#        IE, only accept an NTI if a minimum of 30% of the time slots have actual packets in them.
#            Something about taking a bad image in your thesis write-up or something like that heh ;)

'''
Process:
    1) Ingest pre-processed packet stream
    2) rewrite packet stream into network traffic images using predefined patterns
'''


# In[2]:


capture_src = 'captures_selected'
capture_dst = 'captures_networkTrafficImages'
packet_match_regex = r'(?P<packetTime>\d+-\d+-\d+\W\d+:\d+:\d+\.\d+)\WIP.*proto\W(?P<proto>\w+).*length\W(?P<ipLength>\d+).*\r?\n\W*(?P<srcHost>[\w\.\-]+)\.(?P<srcPort>[\w]+)\W\>\W(?P<dstHost>[\w\.\-]+)\.(?P<dstPort>[\w]+).*length\W(?P<tcpLength>\d+).*'
time_format_string = '%Y-%m-%d %H:%M:%S.%f' #Predefined Time format string used in tcpdump captures


# In[3]:


def get_connection_string(packet):
    return "%s:%s,%s:%s,%s"%(packet.src_host,packet.src_port,packet.dst_host,packet.dst_port,packet.proto)
def get_connection_string_reversed(packet):
    return "%s:%s,%s:%s,%s"%(packet.dst_host,packet.dst_port,packet.src_host,packet.src_port,packet.proto)
def time_string_to_datetime(time_string):
    return datetime.strptime(time_string,time_format_string)
def datetime_to_timestring(datetime_time):
    return datetime_time.strftime(time_format_string)


# In[4]:


class packet:
    packet_string = ""
    src_host = ""
    src_port = ""
    dst_host = ""
    dst_port = ""
    proto = ""
    ip_length = 0
    tcp_length = 0
    packet_time = None
    def __init__(self,src_host,src_port,dst_host,dst_port,proto,packet_string,ip_length,tcp_length,packet_time_str):
        self.src_host = src_host
        self.src_port = src_port
        self.dst_host = dst_host
        self.dst_port = dst_port
        self.proto = proto
        self.packet_string = packet_string
        self.ip_length = int(ip_length)
        self.tcp_length = int(tcp_length)
        self.packet_time = datetime.strptime(packet_time_str,time_format_string)
    def to_string(self):
        print("srcHost:%s\nsrcPort:%s\ndstHost:%s\ndstPort:%s\nproto:%s\n" % (self.src_host,self.src_port,self.dst_host,self.dst_port,self.proto))


# In[5]:


def get_packets_in_file(capture_file):
    line_one = ''
    line_two = ''
    packets = list()
    with open(capture_file,'r') as src:
        for line in src:
            line_one = line_two
            line_two = line
            line_pair = line_one + line_two
            
            packet_match = re.match(packet_match_regex,line_pair,re.MULTILINE)
            if(packet_match):
                cur_packet = packet(packet_match.group('srcHost'),packet_match.group('srcPort'),packet_match.group('dstHost'),packet_match.group('dstPort'),packet_match.group('proto'),line_pair,packet_match.group('ipLength'),packet_match.group('tcpLength'),packet_match.group('packetTime'))
                packets.append(cur_packet)
    return packets


# In[6]:


def create_directory(directory):
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass #We don't care if the directory already exists       
def create_empty_2d_array(array_x,array_y):
    return np.zeros((array_x,array_y),dtype=int) #np arrays are n_rows x n_columns
def write_2d_array_to_file(array_2d,output_file):
    with open(output_file,'w') as nti_file:
        for row in range (0,len(array_2d)):
            for column in range (0,len(array_2d[row])):
                nti_file.write(str(array_2d[row][column]))
                if(column != len(array_2d[row])-1): #Add spaces between elements exceot for last element
                    nti_file.write(" ")
            if(row != len(array_2d)-1): #Add new lines between rows except for last row
                nti_file.write('\n')
def arrange_packets_as_linear_map(packets,array_2d,packet_start_index,packet_end_index):
    x_dim = len(array_2d)
    y_dim = len(array_2d[0])
    #for packet_idx in range (packet_start_index,packet_end_index):
    for row in range (0,x_dim):
        for col in range (0,y_dim):
            array_2d[row][col] = packets[packet_start_index+col+(row*x_dim)].ip_length #ip_packet_length is our targeted feature
    #debug
    #print(array_2d)
    #raise KeyboardInterrupt
def arrange_packets_as_center_spiral(packets,array_2d,packet_start_index,packet_end_index):
    #A center spiral arrangement can be done exactly the same as an edge spiral,
    #  the only difference is that you place the packets backwards
    x_dim = len(array_2d)
    y_dim = len(array_2d[0])
    if(x_dim % 2 == 0 or y_dim % 2 == 0 or x_dim != y_dim): #Dimension sanity check
        print("ERROR: Spiral 2D Array Dimensions must be ODD and have equal x and y dimensions!")
        return
    row_current = 0
    col_current = 0
    packet_index_offset=0
    center_to_edge_distance=min(x_dim,y_dim)//2+min(x_dim,y_dim)%2
    for spiral_level in range (0,center_to_edge_distance):
        #Start inserting elements at the current spiral loop level
        row_current=spiral_level
        col_current=spiral_level
        for orientation in range (0,4): #4 directions (#0==col_right,1==row_down,2==col_left,3==row_up)
            for nElements in range (0,y_dim-(spiral_level*2)):
                if(orientation!=0 and nElements==0): #Direction has changed, skip iteration for current packet!
                    continue
                if(orientation==3 and nElements==1): #Last side has 2 overlaps (side 1 & side 3)
                    continue
                array_2d[row_current][col_current]=packets[packet_end_index-packet_index_offset-1].ip_length
                packet_index_offset += 1
                if(orientation==0):
                    col_current+=1
                elif(orientation==1):
                    row_current+=1
                elif(orientation==2):
                    col_current-=1
                elif(orientation==3):
                    row_current-=1
            #Changing Directions
            if(orientation==0):
                col_current-=1
                row_current+=1
            elif(orientation==1):
                row_current-=1
                col_current-=1
            elif(orientation==2):
                row_current-=1
                col_current+=1
            elif(orientation==3):
                pass #Orientation switching is complete for this cycle!
    #debug
    #print(array_2d)
    #raise KeyboardInterrupt
def arrange_packets_as_edge_spiral(packets,array_2d,packet_start_index,packet_end_index):
    x_dim = len(array_2d)
    y_dim = len(array_2d[0])
    if(x_dim % 2 == 0 or y_dim % 2 == 0 or x_dim != y_dim): #Dimension sanity check
        print("ERROR: Spiral 2D Array Dimensions must be ODD and have equal x and y dimensions!")
        return
    row_current = 0
    col_current = 0
    packet_index_offset=0
    center_to_edge_distance=min(x_dim,y_dim)//2+min(x_dim,y_dim)%2
    for spiral_level in range (0,center_to_edge_distance):
        #Start inserting elements at the current spiral loop level
        row_current=spiral_level
        col_current=spiral_level
        for orientation in range (0,4): #4 directions (#0==col_right,1==row_down,2==col_left,3==row_up)
            for nElements in range (0,y_dim-(spiral_level*2)):
                if(orientation!=0 and nElements==0): #Direction has changed, skip iteration for current packet!
                    continue
                if(orientation==3 and nElements==1): #Last side has 2 overlaps (side 1 & side 3)
                    continue
                array_2d[row_current][col_current]=packets[packet_start_index+packet_index_offset].ip_length
                packet_index_offset += 1
                if(orientation==0):
                    col_current+=1
                elif(orientation==1):
                    row_current+=1
                elif(orientation==2):
                    col_current-=1
                elif(orientation==3):
                    row_current-=1
            #Changing Directions
            if(orientation==0):
                col_current-=1
                row_current+=1
            elif(orientation==1):
                row_current-=1
                col_current-=1
            elif(orientation==2):
                row_current-=1
                col_current+=1
            elif(orientation==3):
                pass #Orientation switching is complete for this cycle!
    #debug
    #print(array_2d)
    #raise KeyboardInterrupt
        
def arrange_packets_as_waterfall(packets,array_2d,packet_start_index,packet_end_index):
    x_dim = len(array_2d)
    y_dim = len(array_2d[0])
    packet_index_offset=0
    #for packet_idx in range (packet_start_index,packet_end_index):
    for row in range (0,x_dim):
        array_2d[row][row] = packets[packet_start_index+packet_index_offset].ip_length #ip_packet_length is our targeted feature
        packet_index_offset += 1
        for val in range (1,row+1):
            array_2d[row-val][row] = packets[packet_start_index+packet_index_offset].ip_length #ip_packet_length is our targeted feature
            packet_index_offset += 1
            array_2d[row][row-val] = packets[packet_start_index+packet_index_offset].ip_length #ip_packet_length is our targeted feature
            packet_index_offset += 1
    #debug
    #print(array_2d)
    #raise KeyboardInterrupt
def arrange_packets_as_diagonal(packets,array_2d,packet_start_index,packet_end_index):
    x_dim = len(array_2d)
    y_dim = len(array_2d[0])
    packet_index_offset=0
    #for packet_idx in range (packet_start_index,packet_end_index):
    for row in range (0,x_dim):
        for val in range (0,row+1):
            array_2d[row-val][val] = packets[packet_start_index+packet_index_offset].ip_length #ip_packet_length is our targeted feature
            packet_index_offset += 1
    for row in range (x_dim-1,-1,-1):       
        for val in range (row-1,-1,-1):
            array_2d[x_dim-row+val][x_dim-val-1] = packets[packet_start_index+packet_index_offset].ip_length #ip_packet_length is our targeted feature
            packet_index_offset += 1
    #debug
    #print(array_2d)
    #raise KeyboardInterrupt
def generate_ntis(packet_list,nti_x,nti_y,output_dir,base_filename,nti_packet_arrangement,max_number_ntis_per_file=999999999999):
    #nti_packet_arrangement can be 'linear','edge_spiral','center_spiral','waterfall','diagonal'
    nti_area = nti_x * nti_y
    cur_packet_list_index = 0
    
    if(len(packet_list)>nti_area):
        create_directory(output_dir)
    
    nti_array = create_empty_2d_array(nti_x,nti_y)
    
    number_ntis_generated = 0
    while((len(packet_list)-cur_packet_list_index) > nti_area and number_ntis_generated < max_number_ntis_per_file ): #Case: There are enough packets to generate a new NTI
        #First fill up the 2d array
        if(nti_packet_arrangement=='linear'):
            arrange_packets_as_linear_map(packets,nti_array,cur_packet_list_index,cur_packet_list_index+nti_area)
        elif(nti_packet_arrangement=='edge_spiral'):
            arrange_packets_as_edge_spiral(packets,nti_array,cur_packet_list_index,cur_packet_list_index+nti_area)
        elif(nti_packet_arrangement=='center_spiral'):
            arrange_packets_as_center_spiral(packets,nti_array,cur_packet_list_index,cur_packet_list_index+nti_area)
        elif(nti_packet_arrangement=='waterfall'):
            arrange_packets_as_waterfall(packets,nti_array,cur_packet_list_index,cur_packet_list_index+nti_area)
        elif(nti_packet_arrangement=='diagonal'):
            arrange_packets_as_diagonal(packets,nti_array,cur_packet_list_index,cur_packet_list_index+nti_area)
        else:
            print("ERROR: Unsupported packet arrangement detected!")
            raise KeyboardInterrupt
        
        #Then Write the 2D array to file (that is the NTI)
        output_nti_file = output_dir + os.sep + base_filename + '.nti-'+str(cur_packet_list_index) + '.nti'
        write_2d_array_to_file(nti_array,output_nti_file)
        
        #Zero out the nti_array for the next NTI to be generated
        nti_array.fill(0) #verified faster than declaring new np.zeros 2d-array
        
        #increment the current NTI index
        cur_packet_list_index += 1
        number_ntis_generated += 1
        
        #debug
        #if(cur_packet_list_index == 300):
        #    raise KeyboardInterrupt


# In[ ]:


def get_packet_indices_for_next_time_interval(packets,current_packet_index,time_interval_end):
    #Function to get the packets for the next NTI time interval
    ##It is assumed that packets are ordered in linearly descending time
    ##It is also assumed that the packets exist within the time interval (IE, no ERROR or Boundary checking is done here!)
    packet_start_index = current_packet_index
    packet_end_index = current_packet_index
    
    while(packets[packet_end_index].packet_time <= time_interval_end):
        packet_end_index+=1 #Another packet is found to be in the NTI
        if packet_end_index == len(packets):
            break
    return packet_start_index,packet_end_index
def get_average_packet_ip_header_length_for_packets(packets,packet_start_index,packet_end_index):
    num_packets = packet_end_index - packet_start_index
    packets_ip_length_total = 0
    for idx in range (packet_start_index,packet_end_index):
        packets_ip_length_total += packets[idx].ip_length
    average_packet_length = 0
    if(num_packets > 0): #Avoid division by zero exception
        average_packet_length = round(packets_ip_length_total / num_packets)
    return average_packet_length
def arrange_packets_as_linear_map_time_based(packets,array_2d,packet_start_index,current_nti_time_interval_start,nti_time_interval):
    x_dim = len(array_2d)
    y_dim = len(array_2d[0])
    
    packets_start_idx = packet_start_index
    packets_end_idx = packet_start_index
    current_nti_time_interval_end = current_nti_time_interval_start + nti_time_interval
    first_interval_packet_index = -1
    #for packet_idx in range (packet_start_index,packet_end_index):
    for row in range (0,x_dim):
        for col in range (0,y_dim):
            packets_start_idx,packets_end_idx = get_packet_indices_for_next_time_interval(packets,packets_start_idx,current_nti_time_interval_end)
            array_2d[row][col] = get_average_packet_ip_header_length_for_packets(packets,packets_start_idx,packets_end_idx)
            #Prepare for next time interval
            packets_start_idx = packets_end_idx
            current_nti_time_interval_end = current_nti_time_interval_end + nti_time_interval
            if(first_interval_packet_index==-1):
                first_interval_packet_index=packets_end_idx
    
    #debug
    #print(array_2d)
    #raise KeyboardInterrupt
    return first_interval_packet_index
    
def arrange_packets_as_edge_spiral_time_based(packets,array_2d,packet_start_index,current_nti_time_interval_start,nti_time_interval):
    x_dim = len(array_2d)
    y_dim = len(array_2d[0])
    if(x_dim % 2 == 0 or y_dim % 2 == 0 or x_dim != y_dim): #Dimension sanity check
        print("ERROR: Spiral 2D Array Dimensions must be ODD and have equal x and y dimensions!")
        return
    
    packets_start_idx = packet_start_index
    packets_end_idx = packet_start_index
    current_nti_time_interval_end = current_nti_time_interval_start + nti_time_interval
    first_interval_packet_index = -1
    
    row_current = 0
    col_current = 0
    packet_index_offset=0
    center_to_edge_distance=min(x_dim,y_dim)//2+min(x_dim,y_dim)%2
    for spiral_level in range (0,center_to_edge_distance):
        #Start inserting elements at the current spiral loop level
        row_current=spiral_level
        col_current=spiral_level
        for orientation in range (0,4): #4 directions (#0==col_right,1==row_down,2==col_left,3==row_up)
            for nElements in range (0,y_dim-(spiral_level*2)):
                if(orientation!=0 and nElements==0): #Direction has changed, skip iteration for current packet!
                    continue
                if(orientation==3 and nElements==1): #Last side has 2 overlaps (side 1 & side 3)
                    continue
                packets_start_idx,packets_end_idx = get_packet_indices_for_next_time_interval(packets,packets_start_idx,current_nti_time_interval_end)
                array_2d[row_current][col_current] = get_average_packet_ip_header_length_for_packets(packets,packets_start_idx,packets_end_idx)
                #Prepare for next time interval
                packets_start_idx = packets_end_idx
                current_nti_time_interval_end = current_nti_time_interval_end + nti_time_interval
                if(first_interval_packet_index==-1):
                    first_interval_packet_index=packets_end_idx
                packet_index_offset += 1
                if(orientation==0):
                    col_current+=1
                elif(orientation==1):
                    row_current+=1
                elif(orientation==2):
                    col_current-=1
                elif(orientation==3):
                    row_current-=1
            #Changing Directions
            if(orientation==0):
                col_current-=1
                row_current+=1
            elif(orientation==1):
                row_current-=1
                col_current-=1
            elif(orientation==2):
                row_current-=1
                col_current+=1
            elif(orientation==3):
                pass #Orientation switching is complete for this cycle!
    #debug
    #print(array_2d)
    #raise KeyboardInterrupt
    return first_interval_packet_index   
def arrange_packets_as_waterfall_time_based(packets,array_2d,packet_start_index,current_nti_time_interval_start,nti_time_interval):
    x_dim = len(array_2d)
    y_dim = len(array_2d[0])
    packet_index_offset=0
    
    packets_start_idx = packet_start_index
    packets_end_idx = packet_start_index
    current_nti_time_interval_end = current_nti_time_interval_start + nti_time_interval
    first_interval_packet_index = -1
    #for packet_idx in range (packet_start_index,packet_end_index):
    for row in range (0,x_dim):
        packets_start_idx,packets_end_idx = get_packet_indices_for_next_time_interval(packets,packets_start_idx,current_nti_time_interval_end)
        array_2d[row][row] = get_average_packet_ip_header_length_for_packets(packets,packets_start_idx,packets_end_idx)
        #Prepare for next time interval
        packets_start_idx = packets_end_idx
        current_nti_time_interval_end = current_nti_time_interval_end + nti_time_interval
        if(first_interval_packet_index==-1):
            first_interval_packet_index=packets_end_idx
        packet_index_offset += 1
        for val in range (1,row+1):
            #Next Time Window
            packets_start_idx,packets_end_idx = get_packet_indices_for_next_time_interval(packets,packets_start_idx,current_nti_time_interval_end)
            array_2d[row-val][row] = get_average_packet_ip_header_length_for_packets(packets,packets_start_idx,packets_end_idx)
            #Prepare for next time interval
            packets_start_idx = packets_end_idx
            current_nti_time_interval_end = current_nti_time_interval_end + nti_time_interval
            #Next Packet
            packets_start_idx,packets_end_idx = get_packet_indices_for_next_time_interval(packets,packets_start_idx,current_nti_time_interval_end)
            array_2d[row][row-val] = get_average_packet_ip_header_length_for_packets(packets,packets_start_idx,packets_end_idx)
            #Prepare for next time interval
            packets_start_idx = packets_end_idx
            current_nti_time_interval_end = current_nti_time_interval_end + nti_time_interval
    #debug
    #print(array_2d)
    return first_interval_packet_index
    #raise KeyboardInterrupt
def arrange_packets_as_diagonal_time_based(packets,array_2d,packet_start_index,current_nti_time_interval_start,nti_time_interval):
    x_dim = len(array_2d)
    y_dim = len(array_2d[0])
    packets_start_idx = packet_start_index
    packets_end_idx = packet_start_index
    current_nti_time_interval_end = current_nti_time_interval_start + nti_time_interval
    first_interval_packet_index = -1
    #for packet_idx in range (packet_start_index,packet_end_index):
    for row in range (0,x_dim):
        for val in range (0,row+1):
            packets_start_idx,packets_end_idx = get_packet_indices_for_next_time_interval(packets,packets_start_idx,current_nti_time_interval_end)
            array_2d[row-val][val] = get_average_packet_ip_header_length_for_packets(packets,packets_start_idx,packets_end_idx)
            #Prepare for next time interval
            packets_start_idx = packets_end_idx
            current_nti_time_interval_end = current_nti_time_interval_end + nti_time_interval
            if(first_interval_packet_index==-1):
                first_interval_packet_index=packets_end_idx
    for row in range (x_dim-1,-1,-1):       
        for val in range (row-1,-1,-1):
            packets_start_idx,packets_end_idx = get_packet_indices_for_next_time_interval(packets,packets_start_idx,current_nti_time_interval_end)
            array_2d[x_dim-row+val][x_dim-val-1] = get_average_packet_ip_header_length_for_packets(packets,packets_start_idx,packets_end_idx)
            #Prepare for next time interval
            packets_start_idx = packets_end_idx
            current_nti_time_interval_end = current_nti_time_interval_end + nti_time_interval
            if(first_interval_packet_index==-1):
                first_interval_packet_index=packets_end_idx
    #debug
    #print(array_2d)
    return first_interval_packet_index
def arrange_packets_as_center_spiral_time_based(packets,array_2d,packet_start_index,current_nti_time_interval_start,nti_time_interval):
    ##I Confess... this is an inefficient time-relative center-spiral implementation... but... IT WORKS!
    ####All of my time relative stuff should be refactored ideally were this to be used in production code!
    #A center spiral arrangement can be done exactly the same as an edge spiral,
    #  the only difference is that you place the packets backwards
    x_dim = len(array_2d)
    y_dim = len(array_2d[0])
    if(x_dim % 2 == 0 or y_dim % 2 == 0 or x_dim != y_dim): #Dimension sanity check
        print("ERROR: Spiral 2D Array Dimensions must be ODD and have equal x and y dimensions!")
        return
    row_current = 0
    col_current = 0

    packets_start_idx = packet_start_index
    packets_end_idx = packet_start_index
    current_nti_time_interval_end = current_nti_time_interval_start + nti_time_interval
    first_interval_packet_index = -1
    
    nti_values_list = list()
    #for packet_idx in range (packet_start_index,packet_end_index):
    for row in range (0,x_dim):
        for col in range (0,y_dim):
            packets_start_idx,packets_end_idx = get_packet_indices_for_next_time_interval(packets,packets_start_idx,current_nti_time_interval_end)
            nti_values_list.append(get_average_packet_ip_header_length_for_packets(packets,packets_start_idx,packets_end_idx))
            #Prepare for next time interval
            packets_start_idx = packets_end_idx
            current_nti_time_interval_end = current_nti_time_interval_end + nti_time_interval
            if(first_interval_packet_index==-1):
                first_interval_packet_index=packets_end_idx
    
    list_offset=0
    #center_to_edge_distance=x_dim//2
    center_to_edge_distance=min(x_dim,y_dim)//2+min(x_dim,y_dim)%2
    #for spiral_level in range (0,center_to_edge_distance+1):
    for spiral_level in range (0,center_to_edge_distance):
        #Start inserting elements at the current spiral loop level
        row_current=spiral_level
        col_current=spiral_level
        for orientation in range (0,4): #4 directions (#0==col_right,1==row_down,2==col_left,3==row_up)
            for nElements in range (0,y_dim-(spiral_level*2)):
                if(orientation!=0 and nElements==0): #Direction has changed, skip iteration for current packet!
                    continue
                if(orientation==3 and nElements==1): #Last side has 2 overlaps (side 1 & side 3)
                    continue
                array_2d[row_current][col_current]=nti_values_list[len(nti_values_list)-list_offset-1]
                list_offset += 1
                if(orientation==0):
                    col_current+=1
                elif(orientation==1):
                    row_current+=1
                elif(orientation==2):
                    col_current-=1
                elif(orientation==3):
                    row_current-=1
            #Changing Directions
            if(orientation==0):
                col_current-=1
                row_current+=1
            elif(orientation==1):
                row_current-=1
                col_current-=1
            elif(orientation==2):
                row_current-=1
                col_current+=1
            elif(orientation==3):
                pass #Orientation switching is complete for this cycle!
    #debug
    #print(array_2d)
    return first_interval_packet_index
    #raise KeyboardInterrupt

def generate_time_relative_ntis(packet_list,nti_x,nti_y,output_dir,base_filename,nti_packet_arrangement,nti_time_range_ms=10000,max_number_ntis_per_file=999999999999):
    #nti_packet_arrangement can be 'linear','edge_spiral','center_spiral','waterfall','diagonal'
    #time_range is the maximum size of the NTI_Area
    nti_area = nti_x * nti_y
    cur_packet_list_index = 0
    nti_start_time = packet_list[cur_packet_list_index].packet_time
    nti_duration = timedelta(milliseconds=nti_time_range_ms)
    nti_interval = nti_duration / nti_area
    nti_ending_time = nti_start_time + nti_duration
        
    if(len(packet_list)>nti_area):
        create_directory(output_dir)
    
    nti_array = create_empty_2d_array(nti_x,nti_y)
    result = 0
    number_ntis_generated = 0

    while(nti_ending_time <= packet_list[len(packet_list)-1].packet_time and number_ntis_generated < max_number_ntis_per_file): #Case: There are enough packets to generate a new NTI
        #First fill up the 2d array
        if(nti_packet_arrangement=='linear'):
            cur_packet_list_index = arrange_packets_as_linear_map_time_based(packets,nti_array,cur_packet_list_index,nti_start_time,nti_interval)
        elif(nti_packet_arrangement=='edge_spiral'):
            cur_packet_list_index = arrange_packets_as_edge_spiral_time_based(packets,nti_array,cur_packet_list_index,nti_start_time,nti_interval)
        elif(nti_packet_arrangement=='center_spiral'):
            cur_packet_list_index = arrange_packets_as_center_spiral_time_based(packets,nti_array,cur_packet_list_index,nti_start_time,nti_interval)
        elif(nti_packet_arrangement=='waterfall'):
            cur_packet_list_index = arrange_packets_as_waterfall_time_based(packets,nti_array,cur_packet_list_index,nti_start_time,nti_interval)
        elif(nti_packet_arrangement=='diagonal'):
            cur_packet_list_index = arrange_packets_as_diagonal_time_based(packets,nti_array,cur_packet_list_index,nti_start_time,nti_interval)
        else:
            print("ERROR: Unsupported packet arrangement detected!")
            raise KeyboardInterrupt
        
        #Then Write the 2D array to file (that is the NTI)
        output_nti_file = output_dir + os.sep + base_filename + '.nti-'+str(cur_packet_list_index) + '.nti'
        write_2d_array_to_file(nti_array,output_nti_file)
        
        #Zero out the nti_array for the next NTI to be generated
        nti_array.fill(0) #verified faster than declaring new np.zeros 2d-array
        
        #Setup NTI Time indices for next NTI
        nti_start_time = nti_start_time + nti_interval
        nti_ending_time = nti_start_time + nti_duration
        number_ntis_generated += 1


# In[ ]:


try:
    capture_dst = "captures_NTIs_Linear_49x49"
    for x in os.walk(capture_src): #each os.walk element is: dirpath, subdir-names, dir-filenames
        outdir = x[0].replace(capture_src,capture_dst)
        try:
            os.mkdir(outdir)
        except FileExistsError:
            pass #We don't care if the directory already exists
        for capture in x[2]:
            if capture.endswith(".cap"):
                base_file = capture[:-4]
                date_file = base_file + '.date'
                src_file = x[0]+os.sep+capture
                output_dir = (x[0]+os.sep+base_file).replace(capture_src,capture_dst)
                #print(src_file)
                #print(output_dir)
                print(base_file)
                packets = get_packets_in_file(src_file)
                
                #debug  to ensure that arrangement code is working as intended
                #for packet_idx in range (0,len(packets)-1):
                #    packets[packet_idx].ip_length = packet_idx
                #end debug for arrangement code testing
                
                #Packet Relative NTIs
                #generate_ntis(packets,5,5,output_dir,base_file,nti_packet_arrangement='linear')
                #generate_ntis(packets,5,5,output_dir,base_file,nti_packet_arrangement='edge_spiral')
                #generate_ntis(packets,21,21,output_dir,base_file,nti_packet_arrangement='center_spiral')
                #generate_ntis(packets,5,5,output_dir,base_file,nti_packet_arrangement='waterfall')
                #generate_ntis(packets,5,5,output_dir,base_file,nti_packet_arrangement='diagonal')
                ##Time Relative NTIs
                #Note that 10000/5x5 == 400ms range per NTI Pixel
                #generate_time_relative_ntis(packets,5,5,output_dir,base_file,nti_packet_arrangement='linear',nti_time_range_ms=10000)
                #generate_time_relative_ntis(packets,5,5,output_dir,base_file,nti_packet_arrangement='linear',nti_time_range_ms=25000)
                #generate_time_relative_ntis(packets,5,5,output_dir,base_file,nti_packet_arrangement='edge_spiral',nti_time_range_ms=10000)
                #generate_time_relative_ntis(packets,5,5,output_dir,base_file,nti_packet_arrangement='waterfall',nti_time_range_ms=25000)
                #generate_time_relative_ntis(packets,5,5,output_dir,base_file,nti_packet_arrangement='diagonal',nti_time_range_ms=25000)
                #generate_time_relative_ntis(packets,5,5,output_dir,base_file,nti_packet_arrangement='center_spiral',nti_time_range_ms=25000)
                
                #raise KeyboardInterrupt
                generate_ntis(packets,49,49,output_dir,base_file,nti_packet_arrangement='linear',max_number_ntis_per_file=20000)
    print("Job Done!")                        
except KeyboardInterrupt:
    print("Execution Stopped due to KeyboardInterrupt")
    pass
            


# In[ ]:


#Isolate the outputs into <src_name>.connectionNumber.cap
##Then plot the connections onto a single graph.
###The dominant connection in a packet capture is the one you keep

