import h5py

# test


with h5py.File('3C90_Pretest_data/test_file_2.h5', 'r') as file:
    print("Keys: ", list(file.keys()))
    B_seq = file['B_seq']
    H_seq = file['H_seq']
    T = file['T']
    Loss = file['Loss']

    B_data = B_seq[:]
    H_data = H_seq[:]
    T_data = T[:]
    Loss_data = Loss[:]