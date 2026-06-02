import h5py

with h5py.File('3C90_Pretest_data/test_file_2.h5', 'r') as file:
    print("Keys: ", list(file.keys()))
    dataset = file['B_seq']
    print("Shape: ", dataset.shape)
    print("Data type: ", dataset.dtype)
    data_array = dataset[:]
    print(data_array)