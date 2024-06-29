# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 23:10:46 2024

@author: HP
"""



import simpy
import random
import pandas as pd

mig_cnt=0
vm_id=1
class DataCenter:
    def __init__(self, env, num_hosts, num_vms_per_host):
        self.env = env
        self.hosts = [Host(env, f"Host-{i+1}", num_vms_per_host) for i in range(num_hosts)]

class Host:
    def __init__(self, env, name, num_vms):
        self.env = env
        self.name = name
        self.vms = [VM(env, f"VM-{vm_id+i}") for i in range(num_vms)]
        global vm_id
        vm_id+=len(self.vms)

class VM:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.memory_usage = 0
        self.faulty_factor=0

class Cloudlet:
    def __init__(self, env, name, length, memory):
        self.env = env
        self.name = name
        self.length = int(length)
        self.memory = float(memory)

def start_simulating(env, data_centre, dataset):
    for index, row in dataset.iterrows():
        name = f"Cloudlet-{index+1}"
        length = row['Length']
        memory = row['Memory']
        
        
        nlength =  (length //1000000) 
        nmemory =  (memory //1000000) 
        nnmemory =  (nmemory //1000000) 
        
        cloudlet = Cloudlet(env, name, nlength,nnmemory)
       # Select the minimum loaded VM in the minimum loaded host
        min_memory_usage = float('inf')
        min_host = None
        for host in data_centre.hosts:
            total_memory_usage = sum(float(vm.memory_usage) for vm in host.vms)
            if total_memory_usage < min_memory_usage:
                min_memory_usage = total_memory_usage
                min_host = host
        
        # Find the minimum loaded VM in the minimum loaded host
        selected_vm = None
        min_memory_usage_vm = float('inf')
        for vm in min_host.vms:
            if vm.memory_usage < min_memory_usage_vm:
                min_memory_usage_vm = vm.memory_usage
                selected_vm = vm
                
        if selected_vm is not None and min_host is not None :        
           env.process(execute_cloudlet(env, data_center,cloudlet,selected_vm,min_host))
        
                
       
         
        yield env.timeout(random.randint(1, 5))


def execute_cloudlet(env,data_center, cloudlet, VM, current_host):
    print(f"{cloudlet.name} arrives at VM {VM.name} in {current_host.name} at time {env.now} with faulty factor {VM.faulty_factor}")
    # Check if the VM has enough memory to execute the cloudlet
    
    if cloudlet.memory + VM.memory_usage > 100.00 :
        rejected_list.append(cloudlet)
        print(f"The Cloudlet {cloudlet.name} is rejected")
        yield env.timeout(0)
    elif cloudlet.memory + VM.memory_usage > 80.00 :
        VM.faulty_factor += 1
        
        # Find the minimum loaded host in the datacenter
        min_host = None
        min_memory_usage = float('inf')
        for host in data_center.hosts:
            total_memory_usage = sum(float(vm.memory_usage) for vm in host.vms)
            if host != current_host and total_memory_usage < min_memory_usage:
                min_memory_usage = total_memory_usage
                min_host = host
                
        #Find if the minimum loaded host is more or less loaded than current_host
        
        if sum(float(vm.memory_usage) for vm in min_host.vms) > sum(float(vm.memory_usage) for vm in current_host.vms) and len(data_center.hosts) > 2:
            # Find the second minimum loaded host in the datacenter
            sec_min_host = None
            sec_min_memory_usage = float('inf')
            for host in data_center.hosts:
              if host != current_host and host != min_host:
                total_memory_usage = sum(float(vm.memory_usage) for vm in host.vms)
                if total_memory_usage < sec_min_memory_usage:
                   sec_min_memory_usage = total_memory_usage
                   sec_min_host = host
                 
            # Find the VM with the lowest faulty_factor in the minimum loaded host
            least_faulty_vm = None
            least_faulty_factor = float('inf')
            for vm in min_host.vms:
                 if vm.faulty_factor < least_faulty_factor:
                     least_faulty_vm = vm
                     least_faulty_factor = vm.faulty_factor                    
           
            # Migrate the least faulty VM to the second least loaded host 
            min_host.vms.remove(least_faulty_vm)
            global mig_cnt
            mig_cnt+=1
            sec_min_host.vms.append(least_faulty_vm)
          
            print(f"The least faulty VM named {least_faulty_vm.name} in {min_host.name} at time {env.now} migrates from  minimum loaded host {min_host.name} to second minimum loaded  {sec_min_host.name}")
            
        # Migrate the current VM to the minimum loaded host
        current_host.vms.remove(VM)
        min_host.vms.append(VM)  
       
        mig_cnt+=1
        print(f"The VM {VM.name} at time {env.now} migrates from  {current_host.name} to {min_host.name}")
        
        # Update the VM's memory usage    
        VM.memory_usage += cloudlet.memory
        # Execute the cloudlet on the new VM
        yield env.timeout(cloudlet.length)
        # Update the VM's memory usage
        VM.memory_usage -= cloudlet.memory
        print(f"{cloudlet.name} finishes execution at time {env.now} on VM {VM.name} in host {min_host.name}")
               
# Create SimPy environment
env = simpy.Environment()
rejected_list = []

# Create data center with 1 DC, 4 hosts, and 10 VMs
data_center = DataCenter(env, num_hosts=3, num_vms_per_host=50)

# # Generate cloudlets
# num_cloudlets = 10
dataset = pd.read_csv('gc_new1.csv',header=0)

#print(dataset.head(10))



env.process(start_simulating(env, data_center, dataset))




# Run simulation
env.run()
print(mig_cnt)
print(len(rejected_list))