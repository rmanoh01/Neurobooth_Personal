#!/usr/bin/env python
# coding: utf-8

# In[42]:


import os 
import glob

def extract_first_39_lines(input_file, output_file):
    with open(input_file, 'rb') as f:
        lines = f.readlines()[:39]
        
    with open(output_file, 'wb') as f:
        f.writelines(lines)
        
def main():
    input_folder = r'C:\Users\rohin\Downloads'
    output_folder = r'C:\Users\rohin\Script outputter'
    
    if os.path.exists(output_folder):
        print(f'File processed previously, skipping step')
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    file_pattern = os.path.join(input_folder, '*.bin')
    files = glob.glob(file_pattern)
    
    for input_file in files:
        filename = os.path.basename(input_file)
        output_file = os.path.join(output_folder, f'condensed_{filename}')
        
        extract_first_39_lines(input_file, output_file)
        print(f'Processed {input_file} and created {output_file}')
    print('All files processed and condensed.')

if __name__ == "__main__":
    main()
    


# In[ ]:




